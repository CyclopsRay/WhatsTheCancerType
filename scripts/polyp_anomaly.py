"""Next step 2 — polyp as the odd one out: learn healthy lining, score how far each cell sits from it.

Leave-one-person-out. For each person with healthy (>=100 cells) and polyp (>=50) samples, train
on the healthy cells of every *other* person in the object, then score all of the held-out
person's cells. Genes (2,000 HVG) are chosen on the training healthy cells only.
Scores (higher = less like healthy):
  scvi   mean distance to the 15 nearest training healthy cells in an scVI latent (no batch key)
  pca    the same in a 30-PC space fitted on the training healthy cells (no deep model)
  nolookalike  1 - share of healthy neighbours in the label-free map (fig10); uses every
         person's labels, so it is a reference point, not a held-out score
Per held-out person and route:
  auroc         polyp cells vs that person's own healthy cells (0.5 = cannot tell)
  auroc_new     inside the polyp: the route's new cells (ASC / SSC) vs the other polyp cells
  top10_new     share of the top-10 % scored polyp cells that are new cells, vs base share
Each cell also gets `pct_own_healthy`: share of the same person's healthy cells scoring lower.

Writes OUT_DIR/anomaly_cells_{obj}.tsv.gz, anomaly_people.tsv, anomaly_states.tsv and
FIG_DIR/fig19_anomaly.png.

Usage: python polyp_anomaly.py DATA_DIR CELLS_DIR LABELFREE_DIR OUT_DIR FIG_DIR [--test]
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scvi
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score
from sklearn.neighbors import NearestNeighbors

from next_common import (OBJECTS, NEW_STATE, INK, MUTED, ROUTE_COLOR, SEED, load_object, lognorm,
                         pick_hvg, counts_adata, style_axes)

KNN = 15
MIN_NORMAL, MIN_POLYP = 100, 50
MAX_TRAIN = 30000


def knn_dist(train, test):
    return NearestNeighbors(n_neighbors=KNN).fit(train).kneighbors(test)[0].mean(1)


def fold(X, names, train, test, epochs, rng):
    hv = pick_hvg(X[train], names, rng=rng)
    L = lognorm(X[:, hv])
    Lt = L[train].toarray()
    mu, sd = Lt.mean(0), Lt.std(0) + 1e-6
    z = lambda M: np.clip((M - mu) / sd, -10, 10)
    pca = PCA(30, random_state=SEED).fit(z(Lt))
    s_pca = knn_dist(pca.transform(z(Lt)), pca.transform(z(L[test].toarray())))

    a = counts_adata(X[train][:, hv], names[hv])
    scvi.model.SCVI.setup_anndata(a)
    m = scvi.model.SCVI(a, n_layers=2, n_latent=10, gene_likelihood="nb")
    m.train(max_epochs=epochs, batch_size=512, early_stopping=True, check_val_every_n_epoch=5,
            enable_progress_bar=False)
    b = counts_adata(X[test][:, hv], names[hv])
    s_scvi = knn_dist(m.get_latent_representation(), m.get_latent_representation(b))
    return s_scvi, s_pca, len(m.history["elbo_train"])


def nolookalike(labelfree_dir, obj, obs):
    f = Path(labelfree_dir) / f"{obj}_embedding.tsv.gz"
    if not f.exists():
        return np.full(len(obs), np.nan)
    e = pd.read_csv(f, sep="\t")
    assert len(e) == len(obs) and (e.donor_id.to_numpy() == obs.donor_id.to_numpy()).all() \
        and (e.Cell_Type.to_numpy() == obs.Cell_Type.to_numpy()).all(), "label-free rows out of order"
    return 1 - e.nbr_normal.to_numpy()


def main(data_dir, cells_dir, labelfree_dir, out_dir, fig_dir, test=False):
    out_dir, fig_dir = Path(out_dir), Path(fig_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scvi.settings.seed = SEED
    rng = np.random.default_rng(SEED)
    tag = "_test" if test else ""
    people_rows, cell_tabs = [], []
    for obj in OBJECTS:
        X, obs, names = load_object(data_dir, cells_dir, obj)
        obs["nolookalike"] = nolookalike(labelfree_dir, obj, obs)
        counts = obs.groupby(["donor_id", "route"]).size().unstack(fill_value=0)
        people = [d for d, r in counts.iterrows() if r.get("normal", 0) >= MIN_NORMAL
                  and max(r.get("conventional", 0), r.get("serrated", 0)) >= MIN_POLYP]
        if test:
            people = people[:2]
        print(obj, "held-out people", len(people), flush=True)
        for p in people:
            train = np.where((obs.route == "normal") & (obs.donor_id != p))[0]
            if len(train) > MAX_TRAIN:
                train = np.sort(rng.choice(train, MAX_TRAIN, replace=False))
            test_ix = np.where(obs.donor_id == p)[0]
            s_scvi, s_pca, ep = fold(X, names, train, test_ix, 3 if test else 150, rng)
            c = obs.iloc[test_ix][["HTAN Specimen ID", "donor_id", "route", "Polyp_Type", "Cell_Type",
                                   "nolookalike"]].copy()
            c["object"], c["scvi"], c["pca"] = obj, s_scvi, s_pca
            hn = c.route == "normal"
            for s in ["scvi", "pca", "nolookalike"]:
                ref = np.sort(c.loc[hn, s].to_numpy())
                c[f"pct_own_healthy_{s}"] = np.searchsorted(ref, c[s].to_numpy()) / max(len(ref), 1)
            cell_tabs.append(c)
            for route in ["conventional", "serrated"]:
                pol = c[c.route == route]
                if len(pol) < MIN_POLYP:
                    continue
                row = dict(object=obj, donor=p, route=route, n_healthy=int(hn.sum()), n_polyp=len(pol),
                           new_share=round((pol.Cell_Type == NEW_STATE[route]).mean(), 3), epochs=ep)
                y = np.r_[np.zeros(hn.sum()), np.ones(len(pol))]
                isnew = (pol.Cell_Type == NEW_STATE[route]).to_numpy()
                for s in ["scvi", "pca", "nolookalike"]:
                    if c[s].isna().all():
                        continue
                    row[f"auroc_{s}"] = round(roc_auc_score(y, np.r_[c.loc[hn, s], pol[s]]), 3)
                    if 5 <= isnew.sum() <= len(pol) - 5:
                        row[f"auroc_new_{s}"] = round(roc_auc_score(isnew, pol[s]), 3)
                    top = pol[s] >= pol[s].quantile(0.9)
                    row[f"top10_new_{s}"] = round(isnew[top.to_numpy()].mean(), 3)
                people_rows.append(row)
                print(row, flush=True)
    people = pd.DataFrame(people_rows)
    people.to_csv(out_dir / f"anomaly_people{tag}.tsv", sep="\t", index=False)
    cells = pd.concat(cell_tabs, ignore_index=True)
    for obj, g in cells.groupby("object"):
        g.to_csv(out_dir / f"anomaly_cells_{obj}{tag}.tsv.gz", sep="\t", index=False)
    states = (cells[cells.route != "normal"].groupby(["route", "Cell_Type"])
              [["pct_own_healthy_scvi", "pct_own_healthy_pca"]].median().round(3)
              .join(cells[cells.route != "normal"].groupby(["route", "Cell_Type"]).size().rename("n")))
    states.to_csv(out_dir / f"anomaly_states{tag}.tsv", sep="\t")
    summarize(people, states)
    figure(people, cells, fig_dir, tag)


def summarize(people, states):
    pd.set_option("display.width", 250)
    for s in ["scvi", "pca", "nolookalike"]:
        if f"auroc_{s}" not in people:
            continue
        for route, g in people.groupby("route"):
            print(f"{s:12s} {route:13s} people {len(g):2d}  AUROC median {g[f'auroc_{s}'].median():.3f} "
                  f"(min {g[f'auroc_{s}'].min():.3f}); >0.7 in {(g[f'auroc_{s}'] > 0.7).sum()}; "
                  f"new-cell AUROC median {g.get(f'auroc_new_{s}', pd.Series(dtype=float)).median():.3f}; "
                  f"top10 new {g[f'top10_new_{s}'].median():.3f} vs base {g.new_share.median():.3f}")
    print(states.to_string())


def figure(people, cells, fig_dir, tag):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=200, gridspec_kw={"width_ratios": [1, 1.4]})
    ax = axes[0]
    scores = [("scvi", "scVI"), ("pca", "PCA"), ("nolookalike", "no look-alike\n(not held out)")]
    jit = np.random.default_rng(SEED)
    for i, (s, lab) in enumerate(scores):
        if f"auroc_{s}" not in people:
            continue
        for j, route in enumerate(["conventional", "serrated"]):
            v = people.loc[people.route == route, f"auroc_{s}"].dropna()
            x = i + (j - 0.5) * 0.3 + jit.uniform(-0.06, 0.06, len(v))
            ax.scatter(x, v, s=28, color=ROUTE_COLOR[route], alpha=0.85, lw=0,
                       label=route if i == 0 else None)
            ax.plot([i + (j - 0.5) * 0.3 - 0.1, i + (j - 0.5) * 0.3 + 0.1], [v.median()] * 2, color=INK, lw=2)
    ax.axhline(0.5, color=MUTED, lw=1, ls="--")
    ax.set_xticks(range(len(scores)), [lab for _, lab in scores])
    ax.set_ylim(0.2, 1.02)
    ax.set_ylabel("AUROC: this person's polyp vs own healthy")
    ax.set_title("A new person, never seen in training", color=INK, loc="left")
    ax.legend(frameon=False, loc="lower right")
    style_axes(ax)
    ax = axes[1]
    pol = cells[cells.route != "normal"]
    order = ["ABS", "GOB", "TAC", "STM", "CT", "TUF", "EE", "ASC", "SSC"]
    w = 0.38
    for j, route in enumerate(["conventional", "serrated"]):
        med = pol[pol.route == route].groupby("Cell_Type").pct_own_healthy_scvi.median().reindex(order)
        ax.bar(np.arange(len(order)) + (j - 0.5) * w, med, w, color=ROUTE_COLOR[route], label=route)
    ax.axhline(0.5, color=MUTED, lw=1, ls="--")
    ax.set_xticks(range(len(order)), order)
    ax.set_ylabel("median score, as share of own healthy cells below it")
    ax.set_title("Which polyp cells look least healthy (scVI score)", color=INK, loc="left")
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(Path(fig_dir) / f"fig19_anomaly{tag}.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--test"]
    main(*a[:5], test="--test" in sys.argv)
