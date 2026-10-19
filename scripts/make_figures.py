"""Midterm / progress-report figures from the derived tables.

Usage: python make_figures.py DERIVED_DIR FIG_DIR
Reads DERIVED_DIR/{pseudobulk,paired,visium}; writes PNGs (200 dpi) to FIG_DIR.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Reference palette, light mode: categorical slots 1-3 + neutral
CONV, SERR, SHARED = "#2a78d6", "#eb6834", "#1baf7a"
NORMAL, NS = "#8d8b85", "#d6d4ce"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e7e6e2"
ROUTE_COLOR = {"normal": NORMAL, "conventional": CONV, "serrated": SERR}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": INK2, "axes.labelcolor": INK,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": False, "figure.dpi": 200, "savefig.bbox": "tight", "legend.frameon": False,
})


def fig_umap(pb, out):
    cells = pd.read_csv(pb / "DIS_cells.tsv.gz", sep="\t")
    cells = cells[cells.route.isin(ROUTE_COLOR)].sample(frac=1, random_state=0)
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    ax = axes[0]
    for r in ["normal", "conventional", "serrated"]:
        c = cells[cells.route == r]
        ax.scatter(c.umap1, c.umap2, s=0.6, c=ROUTE_COLOR[r], lw=0, rasterized=True, label=f"{r} ({len(c):,})")
    ax.set_title("Specimen class", loc="left", color=INK, fontsize=11)
    ax.legend(markerscale=10, loc="upper left", bbox_to_anchor=(0, 0.02), ncol=1, fontsize=8.5, handletextpad=0.1)
    ax = axes[1]
    other = cells[~cells.Cell_Type.isin(["ASC", "SSC"])]
    ax.scatter(other.umap1, other.umap2, s=0.6, c=NS, lw=0, rasterized=True, label="normal-type states")
    for st, col in [("ASC", CONV), ("SSC", SERR)]:
        c = cells[cells.Cell_Type == st]
        ax.scatter(c.umap1, c.umap2, s=0.6, c=col, lw=0, rasterized=True, label=f"{st} ({len(c):,})")
    ax.set_title("Lesion-specific states (Chen 2021 labels)", loc="left", color=INK, fontsize=11)
    ax.legend(markerscale=10, loc="upper left", bbox_to_anchor=(0, 0.02), ncol=1, fontsize=8.5, handletextpad=0.1)
    for ax in axes:
        ax.set_xticks([]); ax.set_yticks([]); ax.spines[:].set_visible(False)
    fig.suptitle(f"DIS epithelium, {len(cells):,} cells from {cells['HTAN Specimen ID'].nunique()} specimens", x=0.01, ha="left", color=INK2, fontsize=9)
    fig.savefig(out / "fig1_umap.png"); plt.close(fig)


def fig_composition(pb, out):
    fig, axes = plt.subplots(1, 4, figsize=(10, 3.4), sharey=False)
    k = 0
    for obj in ["DIS", "VAL"]:
        spec = pd.read_csv(pb / f"{obj}_specimens.tsv", sep="\t").set_index("HTAN Specimen ID")
        comp = pd.read_csv(pb / f"{obj}_composition.tsv", sep="\t", index_col=0)
        frac = 100 * comp.div(comp.sum(1), axis=0)
        for route, state, col in [("conventional", "ASC", CONV), ("serrated", "SSC", SERR)]:
            ax = axes[k]; k += 1
            by = spec.groupby("donor_id").route.agg(set)
            donors = [d for d, r in by.items() if {"normal", route} <= r]
            up = 0
            for d in donors:
                s = spec[spec.donor_id == d]
                n = frac.loc[s.index[s.route == "normal"], state].mean()
                p = frac.loc[s.index[s.route == route], state].mean()
                up += p > n
                ax.plot([0, 1], [n, p], color=col, lw=1.2, alpha=.8)
                ax.scatter([0, 1], [n, p], s=14, color=[NORMAL, col], zorder=3, lw=0)
            ax.set_xticks([0, 1], ["normal", route])
            ax.set_xlim(-0.3, 1.3)
            ax.set_title(f"{obj}: {state}", loc="left", color=INK, fontsize=10.5)
            ax.text(0.02, 0.97, f"up in {up}/{len(donors)} donors", transform=ax.transAxes, va="top",
                    fontsize=8.5, color=INK2)
            if k in (1, 3):
                ax.set_ylabel("% of specimen epithelium")
    fig.suptitle("Within-donor change in lesion-specific state share", x=0.01, ha="left", color=INK2, fontsize=9)
    fig.tight_layout()
    fig.savefig(out / "fig2_composition.png"); plt.close(fig)


CAT_STYLE = [("not significant", NS, "not significant"),
             ("one route, difference not significant", "#a9a7a1", "one route only, difference n.s."),
             ("conventional-specific", CONV, "conventional-specific"),
             ("serrated-specific", SERR, "serrated-specific"),
             ("shared", SHARED, "shared"),
             ("opposite", INK, "opposite direction")]


LABEL_GENES = ["APCDD1", "NKD1", "ASCL2", "MMP7", "TFF1", "TFF2", "ANXA1", "MUC5AC", "REG4", "S100P",
               "AQP8", "CLCA4", "ZG16"]


def fig_route_compare(paired, out, obj="DIS", scope="all"):
    rc = pd.read_csv(paired / f"route_compare_{obj}_{scope}.tsv", sep="\t", index_col=0)
    fig, ax = plt.subplots(figsize=(5.2, 5))
    lim = np.nanpercentile(np.abs(rc[["log2FoldChange_conv", "log2FoldChange_serr"]].values), 99.8)
    for cat, col, lab in CAT_STYLE:
        d = rc[rc.category == cat]
        if len(d):
            ax.scatter(d.log2FoldChange_conv, d.log2FoldChange_serr, s=4 if cat == "not significant" else 7,
                       c=col, lw=0, label=f"{lab} ({len(d):,})", rasterized=True)
    ax.axhline(0, color=GRID, lw=1, zorder=0); ax.axvline(0, color=GRID, lw=1, zorder=0)
    ax.plot([-lim, lim], [-lim, lim], color=GRID, lw=1, ls="--", zorder=0)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    ax.set_xlabel("log2FC polyp vs own normal, conventional")
    ax.set_ylabel("log2FC polyp vs own normal, serrated")
    for g in LABEL_GENES:
        r = rc[rc.gene == g]
        if len(r) and r.category.iloc[0] in ("shared", "conventional-specific", "serrated-specific"):
            r = r.iloc[0]
            if abs(r.log2FoldChange_conv) < lim and abs(r.log2FoldChange_serr) < lim:
                ax.annotate(g, (r.log2FoldChange_conv, r.log2FoldChange_serr), fontsize=8, color=INK,
                            xytext=(4, -3), textcoords="offset points")
    rho = rc[["log2FoldChange_conv", "log2FoldChange_serr"]].corr("spearman").iloc[0, 1]
    ax.set_title(f"{obj} all-epithelium pseudobulk, Spearman ρ = {rho:.2f}", loc="left", color=INK, fontsize=10)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=8, markerscale=2)
    fig.savefig(out / f"fig3_route_compare_{obj}_{scope}.png"); plt.close(fig)


def fig_replication(paired, out):
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 4))
    for ax, route, col in [(axes[0], "conventional", CONV), (axes[1], "serrated", SERR)]:
        d = pd.read_csv(paired / f"de_DIS_{route}_all.tsv", sep="\t", index_col=0)
        v = pd.read_csv(paired / f"de_VAL_{route}_all.tsv", sep="\t", index_col=0)
        s = d[(d.padj < .05) & (d.log2FoldChange.abs() > 1)].index.intersection(v.index)
        x, y = d.loc[s, "log2FoldChange"], v.loc[s, "log2FoldChange"]
        agree = (np.sign(x) == np.sign(y)).mean()
        ax.scatter(x, y, s=6, c=col, lw=0, alpha=.8, rasterized=True)
        ax.axhline(0, color=GRID, lw=1, zorder=0); ax.axvline(0, color=GRID, lw=1, zorder=0)
        ax.set_xlabel("log2FC in DIS (discovery)"); ax.set_ylabel("log2FC in VAL (validation)")
        ax.set_title(f"{route}: {len(s)} DIS hits, {100*agree:.0f}% same sign in VAL", loc="left", color=INK, fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "fig4_replication.png"); plt.close(fig)


def fig_gsea(paired, out, obj="DIS", n=8):
    rows = []
    for route in ["conventional", "serrated"]:
        g = pd.read_csv(paired / f"gsea_{obj}_{route}_all.tsv", sep="\t")
        g["route"] = route
        rows.append(g)
    g = pd.concat(rows)
    g["NES"] = g.NES.astype(float); g["FDR q-val"] = g["FDR q-val"].astype(float)
    top = (g[g["FDR q-val"] < .05].assign(a=lambda x: x.NES.abs()).sort_values("a", ascending=False)
           .Term.drop_duplicates().head(n * 2).tolist())
    piv = g[g.Term.isin(top)].pivot(index="Term", columns="route", values="NES").reindex(columns=["conventional", "serrated"])
    fdr = g[g.Term.isin(top)].pivot(index="Term", columns="route", values="FDR q-val").reindex(columns=["conventional", "serrated"])
    piv = piv.loc[piv.mean(1).sort_values().index]
    fig, ax = plt.subplots(figsize=(6.4, 0.32 * len(piv) + 1))
    y = np.arange(len(piv)); h = 0.38
    for i, (route, col) in enumerate([("conventional", CONV), ("serrated", SERR)]):
        vals = piv[route].values
        hatch = [None if f < .05 else "////" for f in fdr.loc[piv.index, route].values]
        bars = ax.barh(y + (i - .5) * h, vals, height=h, color=col, label=route, edgecolor="white", lw=0.5)
        for b, f in zip(bars, fdr.loc[piv.index, route].values):
            if not f < .05:
                b.set_alpha(0.35)
    ax.set_yticks(y, [t.replace("_", " ") for t in piv.index], fontsize=8.5)
    ax.axvline(0, color=INK2, lw=.8)
    ax.set_xlabel("NES, polyp vs own normal (faded bar: FDR ≥ 0.05)")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title(f"Hallmark GSEA, {obj}", loc="left", color=INK, fontsize=10)
    fig.savefig(out / "fig5_gsea.png"); plt.close(fig)


def fig_visium_auc(vis, out):
    f = vis / "lesion_vs_normal_spots.tsv"
    if not f.exists():
        return
    t = pd.read_csv(f, sep="\t").dropna(subset=["auc"])
    sigs = [("conventional_up", CONV, "conventional-specific up"), ("serrated_up", SERR, "serrated-specific up"),
            ("shared_up", SHARED, "shared up")]
    caps = t.drop_duplicates("capture")[["capture", "tumor_type"]].values.tolist()
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    w = 0.26
    for i, (sig, col, lab) in enumerate(sigs):
        d = t[t.signature == sig].set_index("capture")
        ax.bar(np.arange(len(caps)) + (i - 1) * w, [d.loc[c, "auc"] - 0.5 for c, _ in caps], width=w,
               bottom=0.5, color=col, label=lab, edgecolor="white", lw=1)
    ax.axhline(0.5, color=INK2, lw=.8)
    ax.set_xticks(np.arange(len(caps)), [f"{c.split('_HTA11')[0]}\n{tt}" for c, tt in caps])
    ax.set_ylabel("AUC, lesion vs normal-mucosa spots")
    ax.set_ylim(0.3, 1.0)
    ax.legend(loc="lower center", fontsize=8.5, ncol=3)
    ax.set_title("Visium sections with both lesion and normal mucosa (signatures from DIS scRNA)",
                 loc="left", color=INK, fontsize=10)
    fig.savefig(out / "fig6_visium_auc.png"); plt.close(fig)


def fig_visium(vis, out, cap="8270_2_HTA11_10711", sig="shared_up"):
    f = vis / f"spots_{cap}.tsv.gz"
    if not f.exists():
        return
    s = pd.read_csv(f, sep="\t", index_col=0)
    ann_col = {"adenoma": "#3a3550", "adenoma_border": "#9a95ad", "normal_mucosa": NS}
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4))
    ax = axes[0]
    for a, d in s.groupby("pathology_annotation"):
        ax.scatter(d.x, -d.y, s=9, c=ann_col.get(a, NS), lw=0, label=f"{'lesion' if a == 'adenoma' else a} ({len(d)})")
    ax.legend(fontsize=7.5, loc="lower left", markerscale=1.5)
    ax.set_title("Pathologist spot annotation", loc="left", color=INK, fontsize=10)
    ax = axes[1]
    v = s[sig]; lo, hi = np.nanpercentile(v, [2, 98])
    sc_ = ax.scatter(s.x, -s.y, s=9, c=v, cmap="Blues", vmin=lo, vmax=hi, lw=0)
    fig.colorbar(sc_, ax=ax, fraction=.04, pad=.01).set_label("score")
    ax.set_title(f"{sig.replace('_', ' ')} signature (top 50, from DIS)", loc="left", color=INK, fontsize=10)
    for ax in axes:
        ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([]); ax.spines[:].set_visible(False)
    fig.suptitle(f"Visium {cap} ({s.tumor_type.iloc[0]})", x=0.01, ha="left", color=INK2, fontsize=9)
    fig.savefig(out / f"fig7_visium_{cap}_{sig}.png"); plt.close(fig)


def main(derived, figs):
    derived, figs = Path(derived), Path(figs)
    figs.mkdir(parents=True, exist_ok=True)
    pb, paired, vis = derived / "pseudobulk", derived / "paired", derived / "visium"
    fig_umap(pb, figs); fig_composition(pb, figs)
    if (paired / "route_compare_DIS_all.tsv").exists():
        fig_route_compare(paired, figs); fig_replication(paired, figs); fig_gsea(paired, figs)
    fig_visium_auc(vis, figs)
    fig_visium(vis, figs, "8270_1_HTA11_07862", "conventional_up")
    fig_visium(vis, figs, "8270_5_HTA11_06134", "serrated_up")
    print(sorted(p.name for p in figs.glob("*.png")))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
