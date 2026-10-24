"""Label-free view of the epithelium: our own PCA/UMAP from raw counts, no labels used.

Minimal processing only — per-cell depth normalisation and log (without it PC1 is just
sequencing depth), 2,000 variable genes (MT-/ribosomal excluded), 30 PCs, UMAP.
No batch or donor correction, no cell-type labels. Labels are painted on afterwards.

Per object (DIS, VAL; normal + conventional + serrated cells) writes
  {obj}_embedding.tsv.gz  pc1, pc2, umap1, umap2, and per cell over its 30 nearest
                          neighbours in PC space: share from healthy specimens
                          (`nbr_normal`) and share from the same person (`nbr_same_donor`)
plus the same embedding for the one person with both routes (HTA11_6801, VAL):
  person_6801_embedding.tsv.gz
and figures fig10_label_free_*.png.

Usage: python label_free_view.py DATA_DIR CELLS_DIR OUT_DIR FIG_DIR
"""
import sys
from pathlib import Path

import anndata as ad
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as sp

OBJECTS = {"DIS": "vanderbilt_dis_epithelial.h5ad", "VAL": "vanderbilt_val_epithelial.h5ad"}
ROUTES = ["normal", "conventional", "serrated"]
N_HVG, N_PC, K = 2000, 30, 30
PERSON = "HTA11_6801"
SEED = 0
INK, MUTED = "#1d1a29", "#6e6980"
ROUTE_COLOR = {"normal": "#a9a6b3", "conventional": "#2a78d6", "serrated": "#eb6834"}
ROUTE_LABEL = {"normal": "healthy lining", "conventional": "conventional polyp",
               "serrated": "serrated polyp"}


def read_raw(h):
    g = h["raw/X"]
    return sp.csr_matrix((g["data"][:], g["indices"][:], g["indptr"][:]), shape=tuple(g.attrs["shape"]))


def gene_names(h):
    g = h["raw/var/feature_name"]
    if isinstance(g, h5py.Group):
        return pd.Categorical.from_codes(g["codes"][:], g["categories"][:].astype(str)).astype(str)
    return g[:].astype(str)


def embed(X, names, n_neighbors=15):
    a = ad.AnnData(sp.csr_matrix(X, dtype=np.float32))
    a.var_names = pd.Index(names).astype(str)
    a.var_names_make_unique()
    sc.pp.normalize_total(a, target_sum=1e4)
    sc.pp.log1p(a)
    sc.pp.highly_variable_genes(a, n_top_genes=N_HVG + 300, flavor="seurat")
    bad = a.var_names.str.startswith(("MT-", "RPL", "RPS"))
    hv = np.where(a.var.highly_variable.to_numpy() & ~bad)[0][:N_HVG]
    a = a[:, hv].copy()
    sc.pp.scale(a, max_value=10)
    sc.tl.pca(a, n_comps=N_PC, random_state=SEED)
    sc.pp.neighbors(a, n_neighbors=n_neighbors, random_state=SEED)
    sc.tl.umap(a, random_state=SEED)
    return a.obsm["X_pca"], a.obsm["X_umap"], a.uns["pca"]["variance_ratio"]


def neighbour_shares(P, route, donor):
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=K + 1).fit(P)
    idx = nn.kneighbors(P, return_distance=False)[:, 1:]
    return ((route[idx] == "normal").mean(1), (donor[idx] == donor[:, None]).mean(1))


def scatter(ax, df, col, colors, order, s=0.5, labels=None):
    for k in order:
        c = df[df[col] == k]
        ax.scatter(c.umap1, c.umap2, s=s, c=colors[k], lw=0, rasterized=True,
                   label=f"{(labels or {}).get(k, k)} ({len(c):,})")
    ax.set_axis_off()


def main(data_dir, cells_dir, out_dir, fig_dir):
    data_dir, cells_dir, out_dir, fig_dir = map(Path, (data_dir, cells_dir, out_dir, fig_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    emb = {}
    for obj, fname in OBJECTS.items():
        cells = pd.read_csv(cells_dir / f"{obj}_cells.tsv.gz", sep="\t")
        with h5py.File(data_dir / fname, "r") as h:
            X = read_raw(h)
            names = gene_names(h)
        use = np.where(cells.route.isin(ROUTES).to_numpy())[0]
        P, U, vr = embed(X[use], names)
        df = cells.iloc[use][["HTAN Specimen ID", "donor_id", "route", "Polyp_Type", "Cell_Type"]].copy()
        df[["pc1", "pc2"]], df[["umap1", "umap2"]] = P[:, :2], U
        df["nbr_normal"], df["nbr_same_donor"] = neighbour_shares(
            P, df.route.to_numpy(), df.donor_id.to_numpy())
        df.to_csv(out_dir / f"{obj}_embedding.tsv.gz", sep="\t", index=False)
        emb[obj] = df
        n_don = df.donor_id.nunique()
        print(obj, "cells", len(df), "donors", n_don, "PC1/PC2 var", np.round(vr[:2], 3),
              "same-person neighbours median", round(df.nbr_same_donor.median(), 3),
              "chance ~", round((df.donor_id.value_counts(normalize=True) ** 2).sum(), 3), flush=True)
        if obj == "VAL":
            one = np.where(cells.donor_id.to_numpy()[use] == PERSON)[0]
            P1, U1, _ = embed(X[use[one]], names, n_neighbors=15)
            d1 = df.iloc[one][["HTAN Specimen ID", "route", "Polyp_Type", "Cell_Type"]].copy()
            d1[["umap1", "umap2"]] = U1
            d1.to_csv(out_dir / "person_6801_embedding.tsv.gz", sep="\t", index=False)
            emb["person"] = d1
            print(PERSON, d1.groupby(["HTAN Specimen ID", "route"]).size().to_dict(), flush=True)

    summary(emb, out_dir)
    figures(emb, fig_dir)


def summary(emb, out_dir):
    """Polyp cells with (almost) no healthy neighbours: how many, and which published labels."""
    rows = []
    for obj in ["DIS", "VAL"]:
        df = emb[obj]
        for route in ["conventional", "serrated"]:
            p = df[df.route == route]
            far = p[p.nbr_normal <= 0.05]
            new = "ASC" if route == "conventional" else "SSC"
            rows.append(dict(object=obj, route=route, polyp_cells=len(p),
                             no_healthy_nbr=len(far), pct_no_healthy_nbr=round(100 * len(far) / len(p), 1),
                             pct_of_those_new_label=round(100 * (far.Cell_Type == new).mean(), 1),
                             pct_new_label_in_polyp=round(100 * (p.Cell_Type == new).mean(), 1),
                             pct_new_label_captured=round(100 * (far.Cell_Type == new).sum()
                                                          / max((p.Cell_Type == new).sum(), 1), 1)))
        # Same check for healthy cells: share of normal cells whose neighbours are almost all polyp
        n = df[df.route == "normal"]
        rows.append(dict(object=obj, route="normal", polyp_cells=len(n),
                         no_healthy_nbr=int((n.nbr_normal <= 0.05).sum()),
                         pct_no_healthy_nbr=round(100 * (n.nbr_normal <= 0.05).mean(), 1)))
    t = pd.DataFrame(rows)
    t.to_csv(out_dir / "no_healthy_neighbour_summary.tsv", sep="\t", index=False)
    print(t.to_string(index=False), flush=True)


def figures(emb, fig_dir):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
    rng = np.random.default_rng(SEED)
    for obj in ["DIS", "VAL"]:
        df = emb[obj].sample(frac=1, random_state=SEED)   # random draw order, no class on top
        fig, axes = plt.subplots(1, 3, figsize=(18, 6.4), dpi=200)
        # A: specimen class, all three drawn in random order
        ax = axes[0]
        ax.scatter(df.umap1, df.umap2, s=0.5, c=df.route.map(ROUTE_COLOR), lw=0, rasterized=True)
        for r in ROUTES:
            ax.scatter([], [], s=60, c=ROUTE_COLOR[r], label=f"{ROUTE_LABEL[r]} ({(df.route == r).sum():,})")
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0.0), frameon=False, ncol=1, fontsize=12)
        ax.set_title("Which tissue each cell came from", color=INK, loc="left")
        ax.set_axis_off()
        # B: person
        ax = axes[1]
        donors = df.donor_id.unique()
        pal = plt.get_cmap("tab20")(np.linspace(0, 1, 20))
        cmap = {d: pal[i % 20] for i, d in enumerate(rng.permutation(donors))}
        ax.scatter(df.umap1, df.umap2, s=0.5, c=[cmap[d] for d in df.donor_id], lw=0, rasterized=True)
        ax.set_title(f"Which person ({len(donors)} people)", color=INK, loc="left")
        ax.set_axis_off()
        # C: share of healthy neighbours
        ax = axes[2]
        sc_ = ax.scatter(df.umap1, df.umap2, s=0.5, c=df.nbr_normal, cmap="viridis", vmin=0, vmax=1,
                         lw=0, rasterized=True)
        cb = fig.colorbar(sc_, ax=ax, orientation="horizontal", fraction=0.04, pad=0.02)
        cb.set_label("share of 30 nearest cells from healthy lining", color=MUTED)
        ax.set_title("Has a healthy look-alike?", color=INK, loc="left")
        ax.set_axis_off()
        fig.suptitle(f"{obj}: our own map from raw counts, no labels used", x=0.01, ha="left",
                     color=MUTED, fontsize=13)
        fig.tight_layout()
        fig.savefig(fig_dir / f"fig10_label_free_{obj}.png", facecolor="white")
        plt.close(fig)

        # PCA, same colouring as A
        fig, ax = plt.subplots(figsize=(6.5, 6), dpi=200)
        ax.scatter(df.pc1, df.pc2, s=0.5, c=df.route.map(ROUTE_COLOR), lw=0, rasterized=True)
        ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
        for side in ["top", "right"]:
            ax.spines[side].set_visible(False)
        ax.set_title(f"{obj}: first two principal components", color=INK, loc="left")
        fig.tight_layout()
        fig.savefig(fig_dir / f"fig10_label_free_{obj}_pca.png", facecolor="white")
        plt.close(fig)

    # One person, four specimens
    d1 = emb["person"]
    spec_route = d1.groupby("HTAN Specimen ID").route.first()
    fig, axes = plt.subplots(1, 2, figsize=(13, 6.2), dpi=200)
    ax = axes[0]
    d1s = d1.sample(frac=1, random_state=SEED)
    ax.scatter(d1s.umap1, d1s.umap2, s=4, c=d1s.route.map(ROUTE_COLOR), lw=0, rasterized=True)
    for r in ROUTES:
        ax.scatter([], [], s=60, c=ROUTE_COLOR[r], label=f"{ROUTE_LABEL[r]} ({(d1.route == r).sum():,})")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0.0), frameon=False, fontsize=12)
    ax.set_title("One person: which tissue", color=INK, loc="left")
    ax.set_axis_off()
    ax = axes[1]
    states = d1.Cell_Type.value_counts().index.tolist()
    pal = plt.get_cmap("tab10")
    col = {s: pal(i % 10) for i, s in enumerate(states)}
    col.update({"ASC": "#2a78d6", "SSC": "#eb6834"})
    for s in states:
        c = d1[d1.Cell_Type == s]
        ax.scatter(c.umap1, c.umap2, s=4, color=col[s], lw=0, rasterized=True, label=f"{s} ({len(c):,})")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0.0), frameon=False, ncol=3, fontsize=11,
              markerscale=4)
    ax.set_title("Published cell labels, painted on afterwards", color=INK, loc="left")
    ax.set_axis_off()
    fig.suptitle(f"{PERSON}: {len(spec_route)} samples from one person, map built from these cells only",
                 x=0.01, ha="left", color=MUTED, fontsize=13)
    fig.tight_layout()
    fig.savefig(fig_dir / "fig10_label_free_one_person.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main(*sys.argv[1:5])
