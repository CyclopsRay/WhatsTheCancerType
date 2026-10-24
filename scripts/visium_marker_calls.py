"""Call polyp vs normal Visium spots from a few textbook marker genes; compare with the pathologist.

Marker sets are fixed from the literature, not from our DE:
  conventional  AXIN2, LGR5, ASCL2, NKD1, SOX9, MYC        (Wnt targets)
  serrated      MUC5AC, TFF1, TFF2, ANXA10, AQP5, CLDN18   (gastric metaplasia; Chen 2021 SSC)
  mature        CA1, AQP8, CLCA4, SLC26A3, GUCA2B, MS4A12  (mature colonocytes, lost in polyps)
Per spot: depth-normalise + log1p, mean over each set. Each set is z-scored with mean and SD
pooled over the mucosa spots (adenoma, adenoma_border, normal_mucosa) of all seven captures, so
one rule serves every section:
  polyp_score = max(z_conventional, z_serrated) - z_mature;  polyp if > 0
  route of a polyp spot = the larger of z_conventional, z_serrated
Evaluated on mucosa spots only (muscle and lymphoid spots are left out). Spots are not
independent; per-section numbers are descriptive.

Writes OUT_DIR/marker_calls_spots.tsv.gz, marker_calls_summary.tsv and
FIG_DIR/fig15_visium_marker_calls.png.

Usage: python visium_marker_calls.py ST_DIR OUT_DIR FIG_DIR
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import mannwhitneyu

SETS = {"conventional": ["AXIN2", "LGR5", "ASCL2", "NKD1", "SOX9", "MYC"],
        "serrated": ["MUC5AC", "TFF1", "TFF2", "ANXA10", "AQP5", "CLDN18"],
        "mature": ["CA1", "AQP8", "CLCA4", "SLC26A3", "GUCA2B", "MS4A12"]}
MUCOSA = ["adenoma", "adenoma_border", "normal_mucosa"]
ROUTE_OF = {"TA/TVA": "conventional", "SSL/HP": "serrated"}
INK, MUTED = "#1d1a29", "#6e6980"
COL = {"conventional": "#2a78d6", "serrated": "#eb6834", "normal": "#b4b0bf", "border": "#5b5670",
       "other": "#eeecf2"}


def auc(a, b):
    return mannwhitneyu(a, b).statistic / (len(a) * len(b)) if len(a) >= 10 and len(b) >= 10 else np.nan


def load(st_dir):
    rows = []
    for f in sorted(st_dir.glob("*_master.h5ad")):
        ad = sc.read_h5ad(f)
        ad.var_names_make_unique()
        sc.pp.normalize_total(ad, target_sum=1e4)
        sc.pp.log1p(ad)
        df = pd.DataFrame({"capture": f.name.replace("_master.h5ad", ""),
                           "tumor_type": ad.obs["Tumor Type"].astype(str).to_numpy(),
                           "pathology": ad.obs["pathology_annotation"].astype(str).to_numpy(),
                           "x": ad.obsm["spatial"][:, 0], "y": ad.obsm["spatial"][:, 1]}, index=ad.obs_names)
        for name, genes in SETS.items():
            present = [g for g in genes if g in ad.var_names]
            df[name] = np.asarray(ad[:, present].X.mean(1)).ravel()
            df[f"n_{name}_genes"] = len(present)
        rows.append(df)
        print(df.capture.iloc[0], df.tumor_type.iloc[0], df.pathology.value_counts().to_dict(), flush=True)
    return pd.concat(rows)


def main(st_dir, out_dir, fig_dir):
    st_dir, out_dir, fig_dir = map(Path, (st_dir, out_dir, fig_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    d = load(st_dir)
    muc = d.pathology.isin(MUCOSA)
    for name in SETS:
        mu, sd = d.loc[muc, name].mean(), d.loc[muc, name].std()
        d[f"z_{name}"] = (d[name] - mu) / sd
    d["polyp_score"] = d[["z_conventional", "z_serrated"]].max(1) - d.z_mature
    d["call"] = np.where(d.polyp_score > 0,
                         np.where(d.z_conventional >= d.z_serrated, "conventional", "serrated"), "normal")
    d.loc[~muc, "call"] = "other"
    d.to_csv(out_dir / "marker_calls_spots.tsv.gz", sep="\t")

    rows = []
    for cap, s in d.groupby("capture", sort=False):
        lesion, normal, border = s[s.pathology == "adenoma"], s[s.pathology == "normal_mucosa"], \
            s[s.pathology == "adenoma_border"]
        called = lesion.call != "normal"
        route_calls = lesion.call[called].value_counts()
        row = dict(capture=cap, tumor_type=s.tumor_type.iloc[0], n_lesion=len(lesion), n_normal=len(normal),
                   n_border=len(border),
                   lesion_called_polyp=round(called.mean(), 3) if len(lesion) else np.nan,
                   normal_called_normal=round((normal.call == "normal").mean(), 3) if len(normal) else np.nan,
                   border_called_polyp=round((border.call != "normal").mean(), 3) if len(border) else np.nan,
                   auc_polyp_score=round(auc(lesion.polyp_score, normal.polyp_score), 3),
                   auc_conventional=round(auc(lesion.conventional, normal.conventional), 3),
                   auc_serrated=round(auc(lesion.serrated, normal.serrated), 3),
                   auc_mature_down=round(auc(normal.mature, lesion.mature), 3),
                   route_call=route_calls.idxmax() if len(route_calls) else "",
                   route_call_share=round(route_calls.max() / route_calls.sum(), 3) if len(route_calls) else np.nan,
                   route_truth=ROUTE_OF.get(s.tumor_type.iloc[0], s.tumor_type.iloc[0]))
        if len(lesion) and len(normal):
            both = pd.concat([lesion, normal])
            truth, pred = both.pathology == "adenoma", both.call != "normal"
            row["accuracy"] = round((truth == pred).mean(), 3)
            po, pe = (truth == pred).mean(), truth.mean() * pred.mean() + (1 - truth.mean()) * (1 - pred.mean())
            row["kappa"] = round((po - pe) / (1 - pe), 3)
        rows.append(row)
    t = pd.DataFrame(rows)
    t.to_csv(out_dir / "marker_calls_summary.tsv", sep="\t", index=False)
    pd.set_option("display.width", 250)
    print(t.to_string(index=False), flush=True)
    figure(d, t, fig_dir)


def figure(d, t, fig_dir):
    caps = t.capture.tolist()
    fig, axes = plt.subplots(2, len(caps), figsize=(3.4 * len(caps), 7.4), dpi=200)
    for j, cap in enumerate(caps):
        s = d[d.capture == cap]
        route = ROUTE_OF.get(s.tumor_type.iloc[0], "conventional")
        truth = s.pathology.map({"adenoma": route, "adenoma_border": "border",
                                 "normal_mucosa": "normal"}).fillna("other")
        for i, lab in enumerate([truth, s.call]):
            ax = axes[i, j]
            ax.scatter(s.x, -s.y, s=2.2, c=lab.map(COL), lw=0, rasterized=True)
            ax.set_aspect("equal"); ax.set_axis_off()
        r = t.set_index("capture").loc[cap]
        kind = "conventional" if route == "conventional" else "serrated"
        axes[0, j].set_title(f"{kind} slice\n{cap.split('_')[0]}_{cap.split('_')[1]}", fontsize=12, color=INK)
        sub = f"agree {r.accuracy:.0%}" if pd.notna(r.get("accuracy")) else "no healthy spots"
        axes[1, j].set_title(sub, fontsize=12, color=MUTED)
    axes[0, 0].text(-0.08, 0.5, "pathologist", transform=axes[0, 0].transAxes, rotation=90,
                    va="center", ha="right", fontsize=14, color=INK)
    axes[1, 0].text(-0.08, 0.5, "marker genes", transform=axes[1, 0].transAxes, rotation=90,
                    va="center", ha="right", fontsize=14, color=INK)
    for k, lab in [("normal", "healthy lining"), ("conventional", "conventional polyp"),
                   ("serrated", "serrated polyp"), ("border", "polyp edge (pathologist)"),
                   ("other", "muscle / immune (not scored)")]:
        axes[1, 0].scatter([], [], s=80, c=COL[k], label=lab)
    fig.legend(*axes[1, 0].get_legend_handles_labels(), loc="lower center", ncol=5, frameon=False, fontsize=12)
    fig.tight_layout(rect=(0.02, 0.06, 1, 1))
    fig.savefig(fig_dir / "fig15_visium_marker_calls.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main(*sys.argv[1:4])
