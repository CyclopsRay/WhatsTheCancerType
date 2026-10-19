"""Build specimen-level pseudobulk counts, state composition and cell QC tables.

Reads raw integer counts (`raw/X`) and `obs` straight from the CELLxGENE H5ADs with
h5py, so the dense normalized `X` (several GB) is never loaded. Writes small
tables to OUT_DIR; every downstream analysis starts from these.

Usage (via Slurm): python scripts/build_pseudobulk.py DATA_DIR OUT_DIR
"""
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp

OBJECTS = {"DIS": "vanderbilt_dis_epithelial.h5ad", "VAL": "vanderbilt_val_epithelial.h5ad"}
ROUTE = {"NL": "normal", "AD": "conventional", "SER": "serrated", "UNC": "crc"}
OBS_COLS = ["HTAN Specimen ID", "donor_id", "Sample_Classification", "Polyp_Type",
            "Cell_Type", "tissue", "sex", "disease"]


def read_obs(h, cols):
    out = {}
    for c in cols:
        o = h["obs"][c]
        if isinstance(o, h5py.Group):
            cats = o["categories"][:].astype(str)
            out[c] = pd.Categorical.from_codes(o["codes"][:], cats).astype(str)
        else:
            out[c] = o[:]
    return pd.DataFrame(out)


def read_raw(h):
    g = h["raw/X"]
    shape = tuple(g.attrs["shape"])
    return sp.csr_matrix((g["data"][:], g["indices"][:], g["indptr"][:]), shape=shape)


def group_sum(X, labels):
    codes, uniq = pd.factorize(labels)
    G = sp.csr_matrix((np.ones(len(codes)), (codes, np.arange(len(codes)))),
                      shape=(len(uniq), len(codes)))
    return (G @ X).tocsr(), np.asarray(uniq)


def main(data_dir, out_dir):
    data_dir, out_dir = Path(data_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, fname in OBJECTS.items():
        with h5py.File(data_dir / fname, "r") as h:
            obs = read_obs(h, OBS_COLS)
            genes = pd.DataFrame({
                "gene_id": h["raw/var/_index"][:].astype(str),
                "gene": read_obs_var(h["raw/var"], "feature_name"),
            })
            X = read_raw(h)
            umap = h["obsm/X_umap"][:]
        obs["Polyp_Type"] = obs["Polyp_Type"].replace({"TV": "TVA"})
        obs["route"] = obs["Sample_Classification"].map(ROUTE)
        obs["object"] = name
        spec = obs["HTAN Specimen ID"].to_numpy()

        # Cell QC
        mito = genes["gene"].str.startswith("MT-").to_numpy()
        obs["total_counts"] = np.asarray(X.sum(1)).ravel()
        obs["n_genes"] = np.diff(X.indptr)
        obs["pct_mito"] = 100 * np.asarray(X[:, mito].sum(1)).ravel() / obs["total_counts"]
        obs[["umap1", "umap2"]] = umap[:, :2]
        obs.to_csv(out_dir / f"{name}_cells.tsv.gz", sep="\t", index=False)

        # Specimen metadata
        meta = (obs.groupby("HTAN Specimen ID")
                .agg(donor_id=("donor_id", "first"), route=("route", "first"),
                     Polyp_Type=("Polyp_Type", "first"), tissue=("tissue", "first"),
                     sex=("sex", "first"), n_cells=("donor_id", "size"),
                     median_counts=("total_counts", "median"),
                     median_genes=("n_genes", "median"),
                     median_pct_mito=("pct_mito", "median"))
                .reset_index())
        meta.to_csv(out_dir / f"{name}_specimens.tsv", sep="\t", index=False)

        # State composition: specimen x Cell_Type cell counts
        pd.crosstab(obs["HTAN Specimen ID"], obs["Cell_Type"]).to_csv(
            out_dir / f"{name}_composition.tsv", sep="\t")

        # Pseudobulk: all epithelium per specimen, and per specimen x state
        pb, keys = group_sum(X, spec)
        sp.save_npz(out_dir / f"{name}_pb_specimen.npz", pb)
        pd.Series(keys, name="specimen").to_csv(out_dir / f"{name}_pb_specimen_rows.tsv",
                                                sep="\t", index=False)
        ss = pd.Series(spec).str.cat(obs["Cell_Type"].to_numpy(), sep="|").to_numpy()
        pbs, keys_s = group_sum(X, ss)
        sp.save_npz(out_dir / f"{name}_pb_specimen_state.npz", pbs)
        pd.Series(keys_s, name="specimen_state").to_csv(
            out_dir / f"{name}_pb_specimen_state_rows.tsv", sep="\t", index=False)
        genes.to_csv(out_dir / f"{name}_genes.tsv", sep="\t", index=False)
        print(name, "cells", X.shape[0], "genes", X.shape[1], "specimens", len(keys),
              "specimen-states", len(keys_s), flush=True)


def read_obs_var(g, col):
    o = g[col]
    if isinstance(o, h5py.Group):
        cats = o["categories"][:].astype(str)
        return pd.Categorical.from_codes(o["codes"][:], cats).astype(str)
    return o[:].astype(str)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
