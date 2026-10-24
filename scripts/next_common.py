"""Shared loaders for the four next-step models (person_free, polyp_anomaly, polyp_flow,
visium_mapping): raw counts from the CELLxGENE objects, cell table, gene selection."""
from pathlib import Path

import anndata as ad
import h5py
import numpy as np
import pandas as pd
import scanpy as sc
import scipy.sparse as sp

OBJECTS = {"DIS": "vanderbilt_dis_epithelial.h5ad", "VAL": "vanderbilt_val_epithelial.h5ad"}
NONEPI = "vanderbilt_dis_val_non_epithelial.h5ad"
ROUTES = ["normal", "conventional", "serrated"]
NEW_STATE = {"conventional": "ASC", "serrated": "SSC"}
INK, MUTED = "#1d1a29", "#6e6980"
ROUTE_COLOR = {"normal": "#a9a6b3", "conventional": "#2a78d6", "serrated": "#eb6834"}
ROUTE_LABEL = {"normal": "healthy lining", "conventional": "conventional polyp",
               "serrated": "serrated polyp"}
SEED = 0


def read_raw(h):
    g = h["raw/X"]
    return sp.csr_matrix((g["data"][:], g["indices"][:], g["indptr"][:]), shape=tuple(g.attrs["shape"]))


def obs_col(h, key, where="raw/var"):
    g = h[f"{where}/{key}"]
    if isinstance(g, h5py.Group):
        return pd.Categorical.from_codes(g["codes"][:], g["categories"][:].astype(str)).astype(str)
    return g[:].astype(str)


def load_object(data_dir, cells_dir, obj, routes=ROUTES):
    """Raw counts (CSR, cells x genes) and cell table for the chosen routes, MT-/RP- genes kept."""
    cells = pd.read_csv(Path(cells_dir) / f"{obj}_cells.tsv.gz", sep="\t")
    with h5py.File(Path(data_dir) / OBJECTS[obj], "r") as h:
        X = read_raw(h)
        names = obs_col(h, "feature_name")
    assert X.shape[0] == len(cells)
    use = np.where(cells.route.isin(routes).to_numpy())[0]
    return X[use].astype(np.float32), cells.iloc[use].reset_index(drop=True), pd.Index(names)


def load_nonepi(data_dir):
    with h5py.File(Path(data_dir) / NONEPI, "r") as h:
        X = read_raw(h).astype(np.float32)
        names = obs_col(h, "feature_name")
        meta = pd.DataFrame({k: obs_col(h, k, "obs") for k in ["donor_id", "Cell_Type", "Sample_Classification"]})
    return X, meta, pd.Index(names)


def lognorm(X):
    X = sp.csr_matrix(X, dtype=np.float32)
    tot = np.asarray(X.sum(1)).ravel()
    X = sp.diags(1e4 / np.maximum(tot, 1)) @ X
    X.data = np.log1p(X.data)
    return X


def pick_hvg(X, names, n=2000, rng=None, max_cells=30000):
    """Seurat-flavour HVGs on log-normalised counts of (a subsample of) X; MT-/RPL/RPS excluded."""
    rng = rng or np.random.default_rng(SEED)
    sub = rng.choice(X.shape[0], min(max_cells, X.shape[0]), replace=False)
    a = ad.AnnData(lognorm(X[sub]))
    a.var_names = pd.Index(names).astype(str)
    a.var_names_make_unique()
    sc.pp.highly_variable_genes(a, n_top_genes=n + 300, flavor="seurat")
    bad = np.asarray(pd.Index(names).str.startswith(("MT-", "RPL", "RPS")))
    return np.where(a.var.highly_variable.to_numpy() & ~bad)[0][:n]


def counts_adata(X, names, obs=None):
    a = ad.AnnData(sp.csr_matrix(X, dtype=np.float32), obs=None if obs is None else obs.reset_index(drop=True))
    a.var_names = pd.Index(names).astype(str)
    a.var_names_make_unique()
    a.obs_names = a.obs_names.astype(str)
    return a


def knn_same_share(E, key, k=30, mask=None):
    """Per cell, share of its k nearest neighbours (within `mask` cells) that share `key`."""
    from sklearn.neighbors import NearestNeighbors
    ix = np.arange(len(E)) if mask is None else np.where(mask)[0]
    nn = NearestNeighbors(n_neighbors=k + 1).fit(E[ix])
    idx = nn.kneighbors(E[ix], return_distance=False)[:, 1:]
    kk = np.asarray(key)[ix]
    return (kk[idx] == kk[:, None]).mean(1), (pd.Series(kk).value_counts(normalize=True) ** 2).sum()


def style_axes(ax):
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
