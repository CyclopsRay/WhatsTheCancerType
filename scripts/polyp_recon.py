"""Anomaly v2 — a VAE trained on healthy lining only; polyp cells should reconstruct badly.

Leave-one-person-out, same people and training cells as polyp_anomaly.py: train on the healthy
cells of every other person in the object (<= 30,000), score all cells of the held-out person.
Gene sets (chosen on the training healthy cells only, MT-/RPL/RPS out), one per run:
  hvg       2,000 Seurat HVGs, as in polyp_anomaly.py
  detected  every gene seen in >= 0.1 % of training healthy cells. Keeps genes that are
            nearly silent in healthy lining, which is where most polyp-up genes sit: only 16 % /
            24 % of DIS conventional / serrated up-genes are healthy HVGs.
Model: scVI (2 x 128, 10 latent, NB, observed library), KL warm-up 50 epochs, <= 200 epochs,
early stopping on validation ELBO (10 % of training cells).
Scores per cell (higher = less like healthy):
  recon   NB deviance of the cell's counts under its own reconstruction (posterior-mean latent,
          observed library), summed over genes, divided by the cell's counts over those genes
  latent  mean distance to the 15 nearest training healthy cells in the latent space
Per test: AUROC and AUPRC (polyp vs own healthy), new-cell AUROC / AUPRC inside the polyp, and the
30 genes whose mean deviance rises most from own healthy to polyp (which genes the healthy model
cannot rebuild).

Writes OUT_DIR/recon_people_{genes}.tsv, recon_cells_{obj}_{genes}.tsv.gz,
recon_genes_{genes}.tsv, recon_states_{genes}.tsv and FIG_DIR/fig22_recon_{genes}.png.

Usage: python polyp_recon.py DATA_DIR CELLS_DIR OUT_DIR FIG_DIR {hvg,detected} [--test]
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scvi
import torch
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.neighbors import NearestNeighbors

from next_common import (OBJECTS, NEW_STATE, INK, MUTED, ROUTE_COLOR, SEED, load_object, pick_hvg,
                         counts_adata, style_axes)

KNN, MIN_NORMAL, MIN_POLYP, MAX_TRAIN, MIN_DETECT, TOP_GENES = 15, 100, 50, 30000, 0.001, 30
SCORES = ["recon", "latent"]


def choose_genes(X, names, kind, rng):
    if kind == "hvg":
        return pick_hvg(X, names, rng=rng)
    frac = np.asarray((X > 0).mean(0)).ravel()
    bad = np.asarray(names.str.startswith(("MT-", "RPL", "RPS")))
    return np.where((frac >= MIN_DETECT) & ~bad)[0]


@torch.no_grad()
def encode_and_deviance(model, adata):
    """Posterior-mean latent and per-cell x per-gene NB deviance under the reconstruction."""
    adata = model._validate_anndata(adata)
    mod = model.module
    mod.eval()
    zs, devs = [], []
    for t in model._make_data_loader(adata=adata, batch_size=1024):
        inf = dict(mod.inference(**mod._get_inference_input(t)))
        inf["z"] = inf["qz"].loc
        px = mod.generative(**mod._get_generative_input(t, inf))["px"]
        x = t["X"].to(px.mu.device)
        mu, th = px.mu, px.theta
        t1 = torch.where(x > 0, x * torch.log(x / mu), torch.zeros_like(x))
        t2 = (x + th) * torch.log((x + th) / (mu + th))
        devs.append((2 * (t1 - t2)).clamp(min=0).cpu().numpy().astype(np.float32))
        zs.append(inf["z"].cpu().numpy())
    return np.concatenate(zs), np.concatenate(devs)


def fold(X, names, train, test, kind, test_mode, rng):
    gi = choose_genes(X[train], names, kind, rng)
    a = counts_adata(X[train][:, gi], names[gi])
    scvi.model.SCVI.setup_anndata(a)
    m = scvi.model.SCVI(a, n_layers=2, n_latent=10, gene_likelihood="nb")
    m.train(max_epochs=3 if test_mode else 200, batch_size=512, early_stopping=True,
            check_val_every_n_epoch=5, plan_kwargs={"n_epochs_kl_warmup": 1 if test_mode else 50},
            enable_progress_bar=False)
    z_train = m.get_latent_representation()
    Xt = X[test][:, gi]
    z, dev = encode_and_deviance(m, counts_adata(Xt, names[gi]))
    tot = np.asarray(Xt.sum(1)).ravel()
    recon = dev.sum(1) / np.maximum(tot, 1)
    latent = NearestNeighbors(n_neighbors=KNN).fit(z_train).kneighbors(z)[0].mean(1)
    return recon, latent, dev, names[gi], len(m.history["elbo_train"])


def main(data_dir, cells_dir, out_dir, fig_dir, kind, test=False):
    out_dir, fig_dir = Path(out_dir), Path(fig_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    scvi.settings.seed = SEED
    rng = np.random.default_rng(SEED)
    tag = f"_{kind}" + ("_test" if test else "")
    people_rows, gene_rows, cell_tabs = [], [], []
    for obj in OBJECTS:
        X, obs, names = load_object(data_dir, cells_dir, obj)
        counts = obs.groupby(["donor_id", "route"]).size().unstack(fill_value=0)
        people = [d for d, r in counts.iterrows() if r.get("normal", 0) >= MIN_NORMAL
                  and max(r.get("conventional", 0), r.get("serrated", 0)) >= MIN_POLYP]
        if test:
            people = people[:2]
        print(obj, kind, "held-out people", len(people), flush=True)
        for p in people:
            train = np.where((obs.route == "normal") & (obs.donor_id != p))[0]
            if len(train) > MAX_TRAIN:
                train = np.sort(rng.choice(train, MAX_TRAIN, replace=False))
            tix = np.where(obs.donor_id == p)[0]
            recon, latent, dev, gnames, ep = fold(X, names, train, tix, kind, test, rng)
            c = obs.iloc[tix][["HTAN Specimen ID", "donor_id", "route", "Polyp_Type", "Cell_Type"]].copy()
            c["object"], c["recon"], c["latent"] = obj, recon, latent
            hn = (c.route == "normal").to_numpy()
            for s in SCORES:
                ref = np.sort(c.loc[hn, s].to_numpy())
                c[f"pct_own_healthy_{s}"] = np.searchsorted(ref, c[s].to_numpy()) / max(len(ref), 1)
            cell_tabs.append(c)
            for route in ["conventional", "serrated"]:
                pm = (c.route == route).to_numpy()
                if pm.sum() < MIN_POLYP:
                    continue
                pol = c[pm]
                isnew = (pol.Cell_Type == NEW_STATE[route]).to_numpy()
                y = np.r_[np.zeros(hn.sum()), np.ones(pm.sum())]
                row = dict(object=obj, donor=p, route=route, n_train=len(train), n_genes=len(gnames),
                           n_healthy=int(hn.sum()), n_polyp=int(pm.sum()), epochs=ep,
                           base=round(pm.sum() / (pm.sum() + hn.sum()), 3), new_share=round(isnew.mean(), 3))
                for s in SCORES:
                    v = np.r_[c.loc[hn, s], pol[s]]
                    row[f"auroc_{s}"] = round(roc_auc_score(y, v), 3)
                    row[f"auprc_{s}"] = round(average_precision_score(y, v), 3)
                    if 5 <= isnew.sum() <= len(pol) - 5:
                        row[f"auroc_new_{s}"] = round(roc_auc_score(isnew, pol[s]), 3)
                        row[f"auprc_new_{s}"] = round(average_precision_score(isnew, pol[s]), 3)
                people_rows.append(row)
                print(row, flush=True)
                rise = dev[pm].mean(0) - dev[hn].mean(0)
                top = np.argsort(rise)[::-1][:TOP_GENES]
                gene_rows += [dict(object=obj, donor=p, route=route, rank=k + 1, gene=gnames[j],
                                   dev_rise=round(float(rise[j]), 4)) for k, j in enumerate(top)]
    people = pd.DataFrame(people_rows)
    people.to_csv(out_dir / f"recon_people{tag}.tsv", sep="\t", index=False)
    genes = pd.DataFrame(gene_rows)
    genes.to_csv(out_dir / f"recon_genes{tag}.tsv", sep="\t", index=False)
    cells = pd.concat(cell_tabs, ignore_index=True)
    for obj, g in cells.groupby("object"):
        g.to_csv(out_dir / f"recon_cells_{obj}{tag}.tsv.gz", sep="\t", index=False)
    pol = cells[cells.route != "normal"]
    states = (pol.groupby(["route", "Cell_Type"])[[f"pct_own_healthy_{s}" for s in SCORES]].median().round(3)
              .join(pol.groupby(["route", "Cell_Type"]).size().rename("n")))
    states.to_csv(out_dir / f"recon_states{tag}.tsv", sep="\t")
    summarize(people, genes, states)
    figure(people, cells, fig_dir, kind, tag)


def summarize(people, genes, states):
    pd.set_option("display.width", 250)
    for s in SCORES:
        for route, g in people.groupby("route"):
            gn = g.dropna(subset=[f"auroc_new_{s}"])
            print(f"{s:7s} {route:13s} n={len(g):2d} AUROC median {g[f'auroc_{s}'].median():.3f} "
                  f"(min {g[f'auroc_{s}'].min():.3f}, >0.7 in {(g[f'auroc_{s}'] > 0.7).sum()}) | "
                  f"AUPRC {g[f'auprc_{s}'].median():.3f} vs base {g.base.median():.3f} "
                  f"(lift {(g[f'auprc_{s}'] / g.base).median():.2f}x) | new-cell AUROC "
                  f"{gn[f'auroc_new_{s}'].median():.3f}, AUPRC {gn[f'auprc_new_{s}'].median():.3f} "
                  f"vs base {gn.new_share.median():.3f}")
    for route, g in genes.groupby("route"):
        print(route, "genes most often in a person's top 30:",
              g.gene.value_counts().head(25).to_dict())
    print(states.to_string())


def figure(people, cells, fig_dir, kind, tag):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), dpi=200, gridspec_kw={"width_ratios": [1, 1.4]})
    ax = axes[0]
    jit = np.random.default_rng(SEED)
    labels = {"recon": "reconstruction\nerror", "latent": "distance in\nhidden layer"}
    for i, s in enumerate(SCORES):
        for j, route in enumerate(["conventional", "serrated"]):
            v = people.loc[people.route == route, f"auroc_{s}"]
            x = i + (j - 0.5) * 0.3 + jit.uniform(-0.06, 0.06, len(v))
            ax.scatter(x, v, s=28, color=ROUTE_COLOR[route], alpha=0.85, lw=0, label=route if i == 0 else None)
            ax.plot([i + (j - 0.5) * 0.3 - 0.1, i + (j - 0.5) * 0.3 + 0.1], [v.median()] * 2, color=INK, lw=2)
    ax.axhline(0.5, color=MUTED, lw=1, ls="--")
    ax.set_xticks(range(len(SCORES)), [labels[s] for s in SCORES])
    ax.set_xlim(-0.6, len(SCORES) - 0.4)
    ax.set_ylim(0.2, 1.02)
    ax.set_ylabel("AUROC: this person's polyp vs own healthy")
    ax.set_title(f"Healthy-only VAE, new person ({kind} genes)", color=INK, loc="left")
    ax.legend(frameon=False, loc="lower right")
    style_axes(ax)
    ax = axes[1]
    pol = cells[cells.route != "normal"]
    order = ["ABS", "GOB", "TAC", "STM", "CT", "TUF", "EE", "ASC", "SSC"]
    w = 0.38
    for j, route in enumerate(["conventional", "serrated"]):
        med = pol[pol.route == route].groupby("Cell_Type").pct_own_healthy_recon.median().reindex(order)
        ax.bar(np.arange(len(order)) + (j - 0.5) * w, med, w, color=ROUTE_COLOR[route], label=route)
    ax.axhline(0.5, color=MUTED, lw=1, ls="--")
    ax.set_xticks(range(len(order)), order)
    ax.set_ylabel("median error, as share of own healthy cells below it")
    ax.set_title("Which polyp cells the healthy model cannot rebuild", color=INK, loc="left")
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(Path(fig_dir) / f"fig22_recon{tag}.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--test"]
    main(*a[:5], test="--test" in sys.argv)
