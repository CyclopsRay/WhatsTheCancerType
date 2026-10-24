"""Next step 1 — line up people: a VAE (scVI) that is told whose cell it is and so learns to ignore it.

Per object (DIS, VAL; healthy + conventional + serrated cells), three embeddings:
  pca          30 PCs of log-normalised, scaled HVGs, no correction (the label-free map)
  scvi         scVI, same genes, no person given (does the model alone change anything?)
  scvi_person  scVI with donor_id as the batch key (the person-free model)
and per embedding, kNN (k=30) checks:
  normal_same_person   healthy cells: share of healthy neighbours from the same person (lower = mixed)
  polyp_same_person    polyp cells: same, among polyp cells (part of this may be real clonality)
  new_same_label       ASC + SSC cells: share of neighbours with the same label (higher = routes apart)
  state_agreement      all cells: share of neighbours with the same published label
  new_healthy_nbr      ASC + SSC cells: share of neighbours from healthy lining (low = still no look-alike)
Success = normal_same_person falls toward chance while new_same_label stays high.
Person and batch cannot be told apart here (one processing batch per specimen).

Writes OUT_DIR/{obj}_latent_{model}.npy, {obj}_umap.tsv.gz, person_free_metrics.tsv,
and FIG_DIR/fig18_person_free_{obj}.png.

Usage: python person_free.py DATA_DIR CELLS_DIR OUT_DIR FIG_DIR [--test]
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scanpy as sc
import scvi
import anndata as ad

from next_common import (OBJECTS, NEW_STATE, INK, MUTED, ROUTE_COLOR, ROUTE_LABEL, SEED,
                         load_object, lognorm, pick_hvg, counts_adata, knn_same_share)

K = 30
N_LATENT = 10


def pca_embed(X):
    a = ad.AnnData(lognorm(X))
    sc.pp.scale(a, max_value=10)
    sc.tl.pca(a, n_comps=30, random_state=SEED)
    return a.obsm["X_pca"]


def scvi_embed(X, names, obs, batch_key, max_epochs):
    a = counts_adata(X, names, obs[["donor_id"]])
    scvi.model.SCVI.setup_anndata(a, batch_key=batch_key)
    m = scvi.model.SCVI(a, n_layers=2, n_latent=N_LATENT, gene_likelihood="nb")
    m.train(max_epochs=max_epochs, batch_size=512, early_stopping=True, check_val_every_n_epoch=5,
            enable_progress_bar=False)
    hist = m.history["elbo_validation"].iloc[-1, 0] if "elbo_validation" in m.history else np.nan
    print("  scvi batch_key", batch_key, "epochs", len(m.history["elbo_train"]), "val elbo", hist, flush=True)
    return m.get_latent_representation()


def metrics(E, obs):
    route, donor, state = obs.route.to_numpy(), obs.donor_id.to_numpy(), obs.Cell_Type.to_numpy()
    out = {}
    s, ch = knn_same_share(E, donor, K, route == "normal")
    out.update(normal_same_person=np.median(s), normal_same_person_mean=s.mean(), normal_chance=ch)
    s, ch = knn_same_share(E, donor, K, route != "normal")
    out.update(polyp_same_person=np.median(s), polyp_same_person_mean=s.mean(), polyp_chance=ch)
    new = np.isin(state, ["ASC", "SSC"]) & (route != "normal")
    s, ch = knn_same_share(E, state, K, new)
    out.update(new_same_label=np.median(s), new_same_label_mean=s.mean(), new_chance=ch)
    s, ch = knn_same_share(E, state, K)
    out.update(state_agreement=s.mean(), state_chance=ch)
    healthy = (route == "normal").astype(int)
    from sklearn.neighbors import NearestNeighbors
    idx = NearestNeighbors(n_neighbors=K + 1).fit(E).kneighbors(E[new], return_distance=False)[:, 1:]
    out.update(new_healthy_nbr=healthy[idx].mean(1).mean())
    return {k: round(float(v), 4) for k, v in out.items()}


def umap(E):
    a = ad.AnnData(np.zeros((len(E), 1), dtype=np.float32))
    a.obsm["E"] = E
    sc.pp.neighbors(a, use_rep="E", n_neighbors=15, random_state=SEED)
    sc.tl.umap(a, random_state=SEED)
    return a.obsm["X_umap"]


def main(data_dir, cells_dir, out_dir, fig_dir, test=False):
    out_dir, fig_dir = Path(out_dir), Path(fig_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scvi.settings.seed = SEED
    rows = []
    for obj in OBJECTS:
        X, obs, names = load_object(data_dir, cells_dir, obj)
        if test:
            keep = np.random.default_rng(SEED).choice(len(obs), 8000, replace=False)
            X, obs = X[keep], obs.iloc[keep].reset_index(drop=True)
        hv = pick_hvg(X, names)
        Xh, nh = X[:, hv], names[hv]
        print(obj, "cells", len(obs), "people", obs.donor_id.nunique(), "genes", len(hv), flush=True)
        epochs = 5 if test else 300
        emb = {"pca": pca_embed(Xh),
               "scvi": scvi_embed(Xh, nh, obs, None, epochs),
               "scvi_person": scvi_embed(Xh, nh, obs, "donor_id", epochs)}
        tag = "_test" if test else ""
        for name, E in emb.items():
            np.save(out_dir / f"{obj}_latent_{name}{tag}.npy", E.astype(np.float32))
            m = metrics(E, obs)
            rows.append(dict(object=obj, embedding=name, cells=len(obs), **m))
            print(obj, name, m, flush=True)
        u = obs[["HTAN Specimen ID", "donor_id", "route", "Cell_Type"]].copy()
        for name in ["pca", "scvi_person"]:
            u[[f"{name}_u1", f"{name}_u2"]] = umap(emb[name])
        u.to_csv(out_dir / f"{obj}_umap{tag}.tsv.gz", sep="\t", index=False)
        figure(u, pd.DataFrame(rows), obj, fig_dir, tag)
    t = pd.DataFrame(rows)
    t.to_csv(out_dir / f"person_free_metrics{'_test' if test else ''}.tsv", sep="\t", index=False)
    pd.set_option("display.width", 250)
    print(t.to_string(index=False))


def figure(u, mt, obj, fig_dir, tag):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
    rng = np.random.default_rng(SEED)
    u = u.sample(frac=1, random_state=SEED)
    donors = u.donor_id.unique()
    pal = plt.get_cmap("tab20")(np.linspace(0, 1, 20))
    dcol = {d: pal[i % 20] for i, d in enumerate(rng.permutation(donors))}
    fig, axes = plt.subplots(2, 3, figsize=(18, 12), dpi=150)
    titles = {"pca": "No correction", "scvi_person": "Person removed (scVI)"}
    for r, name in enumerate(["pca", "scvi_person"]):
        m = mt[(mt.object == obj) & (mt.embedding == name)].iloc[0]
        x, y = u[f"{name}_u1"], u[f"{name}_u2"]
        ax = axes[r, 0]
        ax.scatter(x, y, s=0.4, c=u.route.map(ROUTE_COLOR), lw=0, rasterized=True)
        ax.set_title(f"{titles[name]}\nwhich tissue", color=INK, loc="left", fontsize=12)
        ax = axes[r, 1]
        ax.scatter(x, y, s=0.4, c=[dcol[d] for d in u.donor_id], lw=0, rasterized=True)
        ax.set_title(f"Which person\nhealthy cells' neighbours, same person: "
                     f"{100 * m.normal_same_person_mean:.0f}% (chance {100 * m.normal_chance:.0f}%)",
                     color=INK, loc="left", fontsize=12)
        ax = axes[r, 2]
        ax.scatter(x, y, s=0.3, c="#e4e2ea", lw=0, rasterized=True)
        for st, col in [("ASC", ROUTE_COLOR["conventional"]), ("SSC", ROUTE_COLOR["serrated"])]:
            c = u[(u.Cell_Type == st) & (u.route != "normal")]
            ax.scatter(c[f"{name}_u1"], c[f"{name}_u2"], s=0.6, c=col, lw=0, rasterized=True)
        ax.set_title(f"Polyp-only cells: ASC blue, SSC orange\nneighbours with the same label: "
                     f"{100 * m.new_same_label_mean:.0f}%", color=INK, loc="left", fontsize=12)
        for ax in axes[r]:
            ax.set_axis_off()
    for k in ROUTE_LABEL:
        axes[1, 0].scatter([], [], s=60, c=ROUTE_COLOR[k], label=ROUTE_LABEL[k])
    axes[1, 0].legend(loc="upper center", bbox_to_anchor=(0.5, 0.0), frameon=False, ncol=3, fontsize=11)
    fig.suptitle(f"{obj}: {u.donor_id.nunique()} people, {len(u):,} cells", x=0.01, ha="left",
                 color=MUTED, fontsize=13)
    fig.tight_layout()
    fig.savefig(fig_dir / f"fig18_person_free_{obj}{tag}.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--test"]
    main(*a[:4], test="--test" in sys.argv)
