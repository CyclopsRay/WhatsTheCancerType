"""Next step 4 — polyp in the tissue: unmix each Visium spot into single-cell types (DestVI).

For every polyp capture, a reference of single cells is built two ways:
  same    that person's own epithelial cells (healthy + polyp); a published state with < 25 cells
          in that person is topped up with up to 200 cells of that state from other people in the
          same object, so ASC and SSC are always both on offer
  other   epithelial cells of the other people in the same object (no cells from this person)
Both add the non-epithelial cells (T, PLA, B, MYE, FIB, MAS, END; all people, this person's
first, <= 400 per type; excluded from `other` for this person). No smooth-muscle reference exists,
so muscle spots are unmixed into the nearest available types.
Genes: 2,000 HVG of the reference within genes shared with the capture. CondSCVI on the reference,
DestVI on the in-tissue spots, both from scvi-tools.
Per capture and reference:
  mean share of each type per pathology annotation
  auc_new        ASC + SSC share, adenoma spots vs normal-mucosa spots (captures that have both)
  route_call     ASC vs SSC, which is larger summed over adenoma spots, against the pathology route
  spread         normal-mucosa spots: Spearman of ASC + SSC share with distance (in spot spacings)
                 to the nearest adenoma spot, and mean share within 3 spacings vs beyond 10
Writes OUT_DIR/props_{capture}_{ref}.tsv.gz, mapping_by_annotation.tsv, mapping_summary.tsv,
and FIG_DIR/fig21_visium_mapping.png.

Usage: python visium_mapping.py DATA_DIR CELLS_DIR ST_DIR SPOTS_DIR OUT_DIR FIG_DIR [--test]
"""
import re
import sys
from pathlib import Path

import anndata as ad
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.sparse as sp
import scvi
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

from next_common import OBJECTS, INK, MUTED, ROUTE_COLOR, SEED, load_object, load_nonepi, pick_hvg

MIN_TYPE, TOPUP, MAX_TYPE, MAX_NONEPI = 25, 200, 2000, 400
ANNOT_COLOR = {"adenoma": "#1d1a29", "adenoma_border": "#8a6fd1", "normal_mucosa": "#c9c6d3",
               "smooth_muscle": "#e7b46a", "lymphoid_follicle": "#6fb38a"}


def sample_types(idx, labels, cap, rng):
    out = []
    for t in np.unique(labels[idx]):
        ix = idx[labels[idx] == t]
        out.append(ix if len(ix) <= cap else rng.choice(ix, cap, replace=False))
    return np.sort(np.concatenate(out)) if out else np.array([], int)


def first_index(names, genes):
    """Column of the first occurrence of each gene in names."""
    return pd.Series(np.arange(len(names)), index=names)[~names.duplicated()].reindex(genes).to_numpy()


def build_reference(kind, donor, epi, nonepi, st_genes, rng):
    X, obs, names = epi
    state, dn = obs.Cell_Type.to_numpy(), obs.donor_id.to_numpy()
    if kind == "same":
        own = np.where(dn == donor)[0]
        parts = [sample_types(own, state, MAX_TYPE, rng)]
        for t in np.unique(state):
            if (state[own] == t).sum() < MIN_TYPE:
                ix = np.where((dn != donor) & (state == t))[0]
                parts.append(rng.choice(ix, min(TOPUP, len(ix)), replace=False))
        e_ix = np.sort(np.concatenate(parts))
    else:
        e_ix = sample_types(np.where(dn != donor)[0], state, MAX_TYPE, rng)
    Xn, mn, nn = nonepi
    lab_n, dn_n = mn.Cell_Type.to_numpy(), mn.donor_id.to_numpy()
    n_parts = []
    for t in np.unique(lab_n):
        own = np.where((lab_n == t) & (dn_n == donor))[0] if kind == "same" else np.array([], int)
        rest = np.where((lab_n == t) & (dn_n != donor))[0]
        take = min(MAX_NONEPI - min(len(own), MAX_NONEPI), len(rest))
        n_parts.append(np.r_[own[:MAX_NONEPI], rng.choice(rest, take, replace=False)].astype(int))
    n_ix = np.sort(np.concatenate(n_parts))
    genes = names.unique().intersection(nn.unique()).intersection(st_genes)
    gi, gn = first_index(names, genes), first_index(nn, genes)
    Xr = sp.vstack([X[e_ix][:, gi], Xn[n_ix][:, gn]]).tocsr()
    labels = np.r_[state[e_ix], lab_n[n_ix]]
    own_frac = np.r_[dn[e_ix] == donor, dn_n[n_ix] == donor].mean()
    return Xr, labels, genes, own_frac


def spot_spacing(xy):
    d, _ = cKDTree(xy).query(xy, k=2)
    return np.median(d[:, 1])


def run_capture(path, epi_by_obj, nonepi, spots_dir, out_dir, refs, test, rng):
    cap = re.sub(r"_master\.h5ad$", "", path.name)
    donor = "HTA11_" + str(int(re.search(r"HTA11_(\d+)", cap).group(1)))
    obj = next(o for o, (_, obs, _) in epi_by_obj.items() if (obs.donor_id == donor).any())
    st = ad.read_h5ad(path)
    st = st[st.obs.in_tissue.astype(int) == 1].copy()
    st.var_names_make_unique()
    tumor = pd.read_csv(spots_dir / f"spots_{cap}.tsv.gz", sep="\t", usecols=["tumor_type"]).tumor_type.iloc[0]
    truth = "conventional" if tumor.startswith("TA") else "serrated"
    rows, props_out = [], {}
    for kind in refs:
        Xr, labels, genes, own_frac = build_reference(kind, donor, epi_by_obj[obj], nonepi, st.var_names, rng)
        ref = ad.AnnData(Xr.astype(np.float32))
        ref.var_names = genes.astype(str)
        ref.obs["ct"] = pd.Categorical(labels)
        hv = pick_hvg(ref.X, ref.var_names, rng=rng)
        ref = ref[:, hv].copy()
        sta = st[:, ref.var_names].copy()
        sta.X = sp.csr_matrix(sta.X, dtype=np.float32)
        scvi.model.CondSCVI.setup_anndata(ref, labels_key="ct")
        scm = scvi.model.CondSCVI(ref, weight_obs=False)
        scm.train(max_epochs=5 if test else 300, enable_progress_bar=False)
        scvi.model.DestVI.setup_anndata(sta)
        stm = scvi.model.DestVI.from_rna_model(sta, scm)
        stm.train(max_epochs=20 if test else 2500, enable_progress_bar=False)
        P = stm.get_proportions()
        P.index = sta.obs_names
        ann = sta.obs.pathology_annotation.astype(str).to_numpy()
        xy = np.asarray(sta.obsm["spatial"], dtype=float)
        new = P.get("ASC", 0) + P.get("SSC", 0)
        P2 = P.assign(pathology_annotation=ann, x=xy[:, 0], y=xy[:, 1], new_share=new)
        P2.to_csv(out_dir / f"props_{cap}_{kind}{'_test' if test else ''}.tsv.gz", sep="\t")
        props_out[kind] = P2
        r = dict(capture=cap, donor=donor, object=obj, reference=kind, truth=truth, n_ref_cells=len(labels),
                 own_cell_frac=round(own_frac, 3), genes=len(hv), n_spots=len(P),
                 n_adenoma=int((ann == "adenoma").sum()), n_normal=int((ann == "normal_mucosa").sum()))
        aden = ann == "adenoma"
        asc, ssc = P.get("ASC", pd.Series(0, P.index)), P.get("SSC", pd.Series(0, P.index))
        r.update(asc_in_adenoma=round(asc[aden].mean(), 3), ssc_in_adenoma=round(ssc[aden].mean(), 3),
                 route_call="conventional" if asc[aden].sum() > ssc[aden].sum() else "serrated")
        norm = ann == "normal_mucosa"
        if aden.sum() >= 20 and norm.sum() >= 20:
            y = np.r_[np.zeros(norm.sum()), np.ones(aden.sum())]
            r["auc_new"] = round(roc_auc_score(y, np.r_[new[norm], new[aden]]), 3)
            routed = asc if truth == "conventional" else ssc
            r["auc_route_state"] = round(roc_auc_score(y, np.r_[routed[norm], routed[aden]]), 3)
            dist = cKDTree(xy[aden]).query(xy[norm])[0] / spot_spacing(xy)
            rho, pv = spearmanr(dist, new[norm])
            r.update(spread_rho=round(rho, 3), spread_p=float(f"{pv:.3g}"),
                     new_near_le3=round(new[norm][dist <= 3].mean(), 4) if (dist <= 3).any() else np.nan,
                     new_far_gt10=round(new[norm][dist > 10].mean(), 4) if (dist > 10).any() else np.nan,
                     n_near=int((dist <= 3).sum()), n_far=int((dist > 10).sum()))
        rows.append(r)
        print(r, flush=True)
    return rows, props_out


def main(data_dir, cells_dir, st_dir, spots_dir, out_dir, fig_dir, test=False):
    out_dir, fig_dir, st_dir, spots_dir = map(Path, (out_dir, fig_dir, st_dir, spots_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    scvi.settings.seed = SEED
    rng = np.random.default_rng(SEED)
    epi_by_obj = {o: load_object(data_dir, cells_dir, o) for o in OBJECTS}
    for o, (X, obs, names) in epi_by_obj.items():
        epi_by_obj[o] = (X.tocsr(), obs, names)
    nonepi = load_nonepi(data_dir)
    caps = sorted(st_dir.glob("*_master.h5ad"))
    refs = ["same", "other"]
    if test:
        caps, refs = caps[3:4], ["same"]
    rows, all_props = [], {}
    for path in caps:
        r, props = run_capture(path, epi_by_obj, nonepi, spots_dir, out_dir, refs, test, rng)
        rows += r
        all_props[path.name.replace("_master.h5ad", "")] = props
    tag = "_test" if test else ""
    t = pd.DataFrame(rows)
    t.to_csv(out_dir / f"mapping_summary{tag}.tsv", sep="\t", index=False)
    by = []
    for cap, props in all_props.items():
        for kind, P in props.items():
            m = P.drop(columns=["x", "y"]).groupby("pathology_annotation").mean().round(4)
            m.insert(0, "reference", kind)
            m.insert(0, "capture", cap)
            by.append(m.reset_index())
    pd.concat(by).to_csv(out_dir / f"mapping_by_annotation{tag}.tsv", sep="\t", index=False)
    pd.set_option("display.width", 250)
    print(t.to_string(index=False))
    figure(all_props, t, fig_dir, tag)


def figure(all_props, t, fig_dir, tag):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
    caps = list(all_props)
    fig, axes = plt.subplots(len(caps), 3, figsize=(13, 4.2 * len(caps)), dpi=150, squeeze=False)
    for i, cap in enumerate(caps):
        P = all_props[cap]["same"]
        r = t[(t.capture == cap) & (t.reference == "same")].iloc[0]
        ax = axes[i, 0]
        for a, col in ANNOT_COLOR.items():
            c = P[P.pathology_annotation == a]
            ax.scatter(c.x, -c.y, s=6, c=col, lw=0, label=a.replace("_", " ") if i == 0 else None)
        ax.set_title(f"{cap} ({r.truth}): pathologist", color=INK, loc="left", fontsize=11)
        for k, (st, route) in enumerate([("ASC", "conventional"), ("SSC", "serrated")]):
            ax = axes[i, k + 1]
            v = P.get(st, pd.Series(0, P.index))
            ax.scatter(P.x, -P.y, s=6, c=v, cmap="Blues" if st == "ASC" else "Oranges", vmin=0,
                       vmax=max(0.3, float(v.quantile(0.99))), lw=0)
            ax.set_title(f"{st} share (own cells as reference)", color=INK, loc="left", fontsize=11)
        for ax in axes[i]:
            ax.set_aspect("equal")
            ax.set_axis_off()
    axes[0, 0].legend(loc="lower left", bbox_to_anchor=(0, 1.08), frameon=False, ncol=3, fontsize=9,
                      markerscale=2)
    fig.tight_layout()
    fig.savefig(Path(fig_dir) / f"fig21_visium_mapping{tag}.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--test"]
    main(*a[:6], test="--test" in sys.argv)
