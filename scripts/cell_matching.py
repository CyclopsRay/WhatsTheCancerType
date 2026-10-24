"""Step 4 pilot: same-person cell matching with unbalanced optimal transport.

For every donor with a normal specimen and a polyp of a route, couples that donor's
polyp cells (source) to the same donor's normal cells (target) with entropic,
KL-relaxed (unbalanced) OT in a shared PCA space, then reports:

  mapping   share of each polyp state's transported mass landing on each normal state
            (lesion states ASC / SSC are the question; polyp ABS/GOB/TAC/STM -> same
            normal state is the positive control)
  matched   transported mass per source cell relative to its input mass; cells with no
            good counterpart in the normal tissue keep less mass (unbalanced OT)
  cross     transport cost per unit mass to the donor's own normal vs to every other
            donor's normal in the same object (is the own lining the closest match?)

A coupling is resemblance in expression space, not lineage.
Cost = squared Euclidean distance in a 30-PC space fitted per object, divided by the
median squared distance between random cell pairs; MT- and ribosomal genes excluded.
Settings: main eps=0.05, rho=1; sensitivity eps in {0.02, 0.1} x rho in {0.3, 3}.

Usage: python cell_matching.py DATA_DIR CELLS_DIR OUT_DIR N_JOBS [--test]
"""
import sys
import zlib
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import scanpy as sc
import anndata as ad
import scipy.sparse as sp
from scipy.special import logsumexp
from sklearn.decomposition import PCA
from joblib import Parallel, delayed

OBJECTS = {"DIS": "vanderbilt_dis_epithelial.h5ad", "VAL": "vanderbilt_val_epithelial.h5ad"}
ROUTES = ["conventional", "serrated"]
N_HVG, N_PC = 2000, 30
N_SELF, N_CROSS = 2000, 800          # max cells per side
MIN_POLYP, MIN_NORMAL, MIN_STATE = 50, 100, 20
MAIN = (0.05, 1.0)
GRID = [(0.02, 0.3), (0.02, 3.0), (0.1, 0.3), (0.1, 3.0)]
SEED = 0


def read_raw(h):
    g = h["raw/X"]
    return sp.csr_matrix((g["data"][:], g["indices"][:], g["indptr"][:]), shape=tuple(g.attrs["shape"]))


def lognorm(X):
    X = sp.csr_matrix(X, dtype=np.float32)
    tot = np.asarray(X.sum(1)).ravel()
    X = sp.diags(1e4 / np.maximum(tot, 1)) @ X
    X.data = np.log1p(X.data)
    return X


def embed_object(data_dir, cells_dir, obj, rng):
    cells = pd.read_csv(cells_dir / f"{obj}_cells.tsv.gz", sep="\t")
    with h5py.File(data_dir / OBJECTS[obj], "r") as h:
        X = read_raw(h)
        gid = h["raw/var/feature_name"]
        if isinstance(gid, h5py.Group):
            names = pd.Categorical.from_codes(gid["codes"][:], gid["categories"][:].astype(str)).astype(str)
        else:
            names = gid[:].astype(str)
    names = pd.Index(names)
    assert X.shape[0] == len(cells)
    use = cells.route.isin(["normal"] + ROUTES).to_numpy()
    idx = np.where(use)[0]
    L = lognorm(X[idx])
    # HVGs on a subsample, excluding mito and ribosomal genes
    sub = rng.choice(L.shape[0], min(30000, L.shape[0]), replace=False)
    a = ad.AnnData(L[sub])
    a.var_names = names.astype(str)
    a.var_names_make_unique()
    sc.pp.highly_variable_genes(a, n_top_genes=N_HVG + 300, flavor="seurat")
    bad = names.str.startswith(("MT-", "RPL", "RPS"))
    hv = np.where(a.var.highly_variable.to_numpy() & ~np.asarray(bad))[0][:N_HVG]
    Lh = L[:, hv].toarray()
    mu, sd = Lh[sub].mean(0), Lh[sub].std(0) + 1e-6
    Z = np.clip((Lh - mu) / sd, -10, 10)
    pca = PCA(N_PC, random_state=SEED).fit(Z[sub])
    E = pca.transform(Z).astype(np.float64)
    i, j = rng.integers(0, len(E), 20000), rng.integers(0, len(E), 20000)
    scale = np.median(((E[i] - E[j]) ** 2).sum(1))
    meta = cells.iloc[idx].reset_index(drop=True)
    print(obj, "cells embedded", len(E), "HVG", len(hv), "PC var", round(pca.explained_variance_ratio_.sum(), 3),
          "cost scale", round(scale, 2), flush=True)
    return meta, E, scale


def uot(C, eps, rho, n_iter=3000, tol=1e-7):
    """Log-domain unbalanced Sinkhorn, uniform marginals, KL marginal penalty rho."""
    n, m = C.shape
    loga, logb = np.full(n, -np.log(n)), np.full(m, -np.log(m))
    f, g = np.zeros(n), np.zeros(m)
    tau = rho / (rho + eps)
    Ce = -C / eps
    for _ in range(n_iter):
        f_new = -tau * eps * logsumexp(Ce + (g / eps + logb)[None, :], axis=1)
        g_new = -tau * eps * logsumexp(Ce + (f_new / eps + loga)[:, None], axis=0)
        err = max(np.abs(f_new - f).max(), np.abs(g_new - g).max())
        f, g = f_new, g_new
        if err < tol:
            break
    return np.exp(Ce + (f / eps + loga)[:, None] + (g / eps + logb)[None, :])


def sqdist(A, B, scale):
    return np.maximum((A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2 * A @ B.T, 0) / scale


def pick(ix, n, seed):
    return ix if len(ix) <= n else np.random.default_rng(seed).choice(ix, n, replace=False)


def self_task(obj, route, donor, src, tgt, E, states, scale, settings):
    C = sqdist(E[src], E[tgt], scale)
    s_lab, t_lab = states[src], states[tgt]
    maps, matched = [], []
    for eps, rho in settings:
        P = uot(C, eps, rho)
        row = P.sum(1)
        ratio = row * len(src)                     # transported / input mass per cell
        T = pd.DataFrame({t: P[:, t_lab == t].sum(1) for t in np.unique(t_lab)})
        for s in np.unique(s_lab):
            m = s_lab == s
            if m.sum() < MIN_STATE:
                continue
            frac = T[m].sum(0) / row[m].sum()
            for t, v in frac.items():
                maps.append(dict(object=obj, route=route, donor=donor, eps=eps, rho=rho,
                                 source_state=s, n_source=int(m.sum()), target_state=t,
                                 n_target=int((t_lab == t).sum()), mass_frac=v,
                                 enrichment=v / ((t_lab == t).mean())))
            matched.append(dict(object=obj, route=route, donor=donor, eps=eps, rho=rho,
                                source_state=s, n_source=int(m.sum()),
                                mean_matched=ratio[m].mean(), median_matched=np.median(ratio[m])))
    return maps, matched


def cross_task(obj, route, donor, src, targets, E, scale, eps, rho):
    out = []
    for tdonor, tgt in targets.items():
        C = sqdist(E[src], E[tgt], scale)
        P = uot(C, eps, rho)
        out.append(dict(object=obj, route=route, donor=donor, target_donor=tdonor,
                        is_self=tdonor == donor, cost_per_mass=(P * C).sum() / P.sum(),
                        total_mass=P.sum()))
    return out


def main(data_dir, cells_dir, out_dir, n_jobs, test=False):
    data_dir, cells_dir, out_dir = Path(data_dir), Path(cells_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    maps, matched, cross = [], [], []
    for obj in OBJECTS:
        meta, E, scale = embed_object(data_dir, cells_dir, obj, rng)
        states = meta.Cell_Type.to_numpy()
        normal_by_donor = {d: g.index.to_numpy() for d, g in meta[meta.route == "normal"].groupby("donor_id")}
        normal_by_donor = {d: ix for d, ix in normal_by_donor.items() if len(ix) >= MIN_NORMAL}
        self_jobs, cross_jobs = [], []
        for route in ROUTES:
            for d, g in meta[meta.route == route].groupby("donor_id"):
                if d not in normal_by_donor or len(g) < MIN_POLYP:
                    continue
                k = zlib.crc32(f"{obj}|{route}|{d}".encode()) % 10000
                src = pick(g.index.to_numpy(), N_SELF, k)
                tgt = pick(normal_by_donor[d], N_SELF, k + 1)
                settings = [MAIN] if test else [MAIN] + GRID
                self_jobs.append(delayed(self_task)(obj, route, d, src, tgt, E, states, scale, settings))
                srcc = pick(g.index.to_numpy(), N_CROSS, k + 2)
                targets = {t: pick(ix, N_CROSS, k + 3) for t, ix in normal_by_donor.items()}
                if test:
                    targets = dict(list({d: targets[d]}.items()) + list(targets.items())[:3])
                cross_jobs.append(delayed(cross_task)(obj, route, d, srcc, targets, E, scale, *MAIN))
        if test:
            self_jobs, cross_jobs = self_jobs[:2], cross_jobs[:2]
        print(obj, "donor-route tasks", len(self_jobs), flush=True)
        for m, mt in Parallel(n_jobs=n_jobs)(self_jobs):
            maps += m
            matched += mt
        for c in Parallel(n_jobs=n_jobs)(cross_jobs):
            cross += c
        print(obj, "done", flush=True)

    maps, matched, cross = pd.DataFrame(maps), pd.DataFrame(matched), pd.DataFrame(cross)
    tag = "_test" if test else ""
    maps.to_csv(out_dir / f"cm_mapping{tag}.tsv", sep="\t", index=False)
    matched.to_csv(out_dir / f"cm_matched{tag}.tsv", sep="\t", index=False)
    cross.to_csv(out_dir / f"cm_cross{tag}.tsv", sep="\t", index=False)
    summarize(maps, matched, cross)


def summarize(maps, matched, cross):
    pd.set_option("display.width", 200)
    main = maps[(maps.eps == MAIN[0]) & (maps.rho == MAIN[1])]
    top = main.loc[main.groupby(["object", "route", "donor", "source_state"]).mass_frac.idxmax()]
    print("\nTop normal target per donor, main setting")
    for (route, s), g in top.groupby(["route", "source_state"]):
        print(f"  {route:12s} {s:4s} donors {len(g):2d}: " + ", ".join(f"{k} {v}" for k, v in g.target_state.value_counts().items()))
    print("\nTop normal target by enrichment (mass share / target share), normal states with >=20 cells")
    big = main[main.n_target >= MIN_STATE]
    topE = big.loc[big.groupby(["object", "route", "donor", "source_state"]).enrichment.idxmax()]
    for (route, s), g in topE.groupby(["route", "source_state"]):
        print(f"  {route:12s} {s:4s} donors {len(g):2d}: " + ", ".join(f"{k} {v}" for k, v in g.target_state.value_counts().items()))
    print("\nMedian mass fraction to each normal state (lesion states)")
    les = main[((main.route == "conventional") & (main.source_state == "ASC")) |
               ((main.route == "serrated") & (main.source_state == "SSC"))]
    print(les.pivot_table(index="source_state", columns="target_state", values="mass_frac", aggfunc="median").round(3).to_string())
    print("Median enrichment (lesion states, targets >=20 cells)")
    print(les[les.n_target >= MIN_STATE].pivot_table(index="source_state", columns="target_state", values="enrichment", aggfunc="median").round(2).to_string())
    print("\nPositive control: polyp state -> same normal state, median mass fraction")
    ctl = main[main.source_state == main.target_state]
    print(ctl.groupby("source_state").mass_frac.agg(["median", "size"]).round(3).to_string())
    print("\nSensitivity: lesion top target per setting")
    for (eps, rho), g in maps.groupby(["eps", "rho"]):
        t = g.loc[g.groupby(["object", "route", "donor", "source_state"]).mass_frac.idxmax()]
        a = t[(t.route == "conventional") & (t.source_state == "ASC")].target_state.value_counts()
        s = t[(t.route == "serrated") & (t.source_state == "SSC")].target_state.value_counts()
        gb = g[g.n_target >= MIN_STATE]
        tE = gb.loc[gb.groupby(["object", "route", "donor", "source_state"]).enrichment.idxmax()]
        aE = tE[(tE.route == "conventional") & (tE.source_state == "ASC")].target_state.value_counts()
        sE = tE[(tE.route == "serrated") & (tE.source_state == "SSC")].target_state.value_counts()
        print(f"  eps {eps} rho {rho}: by mass ASC {dict(a)} SSC {dict(s)} | by enrichment ASC {dict(aE)} SSC {dict(sE)}")
    print("\nMatched mass (1 = fully matched), main setting, median over donors")
    mm = matched[(matched.eps == MAIN[0]) & (matched.rho == MAIN[1])]
    print(mm.pivot_table(index="source_state", columns="route", values="mean_matched", aggfunc="median").round(3).to_string())
    rows = []
    for (o, r, d), g in mm.groupby(["object", "route", "donor"]):
        les = "ASC" if r == "conventional" else "SSC"
        if les in g.source_state.values:
            other = g[~g.source_state.isin(["ASC", "SSC"])].mean_matched.median()
            rows.append(g[g.source_state == les].mean_matched.iloc[0] < other)
    print(f"  lesion state less matched than the donor's other polyp states: {sum(rows)} / {len(rows)} donor-routes")
    print("\nOwn normal vs other donors' normal: rank of own by cost per unit mass")
    rk = []
    for (o, r, d), g in cross.groupby(["object", "route", "donor"]):
        g = g.sort_values("cost_per_mass").reset_index(drop=True)
        rk.append(dict(object=o, route=r, donor=d, n=len(g), rank=int(g.index[g.is_self][0]) + 1))
    rk = pd.DataFrame(rk)
    print(f"  own normal is the cheapest match: {(rk['rank'] == 1).sum()} / {len(rk)}; "
          f"median rank {rk['rank'].median()} of median {rk.n.median()} candidates; "
          f"chance ~{(1 / rk.n).sum():.1f}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--test"]
    main(*args[:3], int(args[3]), test="--test" in sys.argv)
