"""Stem score and mature-absorptive score per cell, from raw counts.

Score = mean log2(CPM + 1) over a fixed marker set, the same sets as `marker_check.py`:
  stem    LGR5, OLFM4, SMOC2, ASCL2           (STM markers)
  mature  CA1, SLC26A3, AQP8, CEACAM7         (ABS markers)
Writes, per object, {obj}_crypt_scores.tsv.gz (one row per cell) and
crypt_scores_person.tsv: per person x tissue x Cell_Type median of each score
(groups with >= 20 cells).

Usage: python crypt_axis_scores.py DATA_DIR CELLS_DIR OUT_DIR
"""
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
import scipy.sparse as sp

OBJECTS = {"DIS": "vanderbilt_dis_epithelial.h5ad", "VAL": "vanderbilt_val_epithelial.h5ad"}
SETS = {"stem": ["LGR5", "OLFM4", "SMOC2", "ASCL2"], "mature": ["CA1", "SLC26A3", "AQP8", "CEACAM7"]}
MIN_CELLS = 20


def read_raw(h):
    g = h["raw/X"]
    return sp.csr_matrix((g["data"][:], g["indices"][:], g["indptr"][:]), shape=tuple(g.attrs["shape"]))


def main(data_dir, cells_dir, out_dir):
    data_dir, cells_dir, out_dir = map(Path, (data_dir, cells_dir, out_dir))
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for obj, fname in OBJECTS.items():
        cells = pd.read_csv(cells_dir / f"{obj}_cells.tsv.gz", sep="\t")
        genes = pd.read_csv(cells_dir / f"{obj}_genes.tsv", sep="\t")
        with h5py.File(data_dir / fname, "r") as h:
            X = read_raw(h)
        lib = np.asarray(X.sum(1)).ravel()
        df = cells[["HTAN Specimen ID", "donor_id", "route", "Cell_Type"]].copy()
        for name, gs in SETS.items():
            cols = [np.where(genes.gene.to_numpy() == g)[0][0] for g in gs]
            M = np.asarray(X[:, cols].todense()) / lib[:, None] * 1e6
            df[name] = np.log2(M + 1).mean(1)
        df = df[df.route.isin(["normal", "conventional", "serrated"])]
        df.to_csv(out_dir / f"{obj}_crypt_scores.tsv.gz", sep="\t", index=False)
        g = df.groupby(["donor_id", "route", "Cell_Type"])
        med = g[["stem", "mature"]].median().assign(n=g.size()).reset_index()
        rows.append(med[med.n >= MIN_CELLS].assign(object=obj))
        print(obj, df.groupby(["route", "Cell_Type"])[["stem", "mature"]].median().round(2).to_string(), flush=True)
    pd.concat(rows).to_csv(out_dir / "crypt_scores_person.tsv", sep="\t", index=False)


if __name__ == "__main__":
    main(*sys.argv[1:4])
