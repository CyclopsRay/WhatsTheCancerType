"""Marker check of the published Cell_Type labels on specimen x state pseudobulk.

For each object, mean log-CPM per state over specimen x state groups with >=30 cells,
then z-scored across states per gene. A label is supported when its canonical markers
peak in it.

Usage: python marker_check.py PB_DIR OUT_DIR
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

MIN_CELLS = 30
MARKERS = {
    "STM": ["LGR5", "OLFM4", "SMOC2", "ASCL2"],
    "TAC": ["MKI67", "TOP2A", "PCNA"],
    "ABS": ["CA1", "SLC26A3", "AQP8", "CEACAM7"],
    "GOB": ["MUC2", "TFF3", "SPINK4", "FCGBP"],
    "EE": ["CHGA", "CHGB", "PYY"],
    "TUF": ["POU2F3", "TRPM5", "SH2D6"],
    "CT": ["BEST4", "OTOP2", "CA7"],
    "ASC": ["LGR5", "ASCL2", "SOX9", "MYC"],
    "SSC": ["MUC5AC", "TFF1", "ANXA10", "AQP5"],
}


def main(pb_dir, out_dir):
    pb_dir, out_dir = Path(pb_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for obj in ["DIS", "VAL"]:
        genes = pd.read_csv(pb_dir / f"{obj}_genes.tsv", sep="\t")
        comp = pd.read_csv(pb_dir / f"{obj}_composition.tsv", sep="\t", index_col=0)
        keys = pd.read_csv(pb_dir / f"{obj}_pb_specimen_state_rows.tsv", sep="\t")["specimen_state"]
        X = sp.load_npz(pb_dir / f"{obj}_pb_specimen_state.npz").tocsr()
        spec, state = keys.str.split("|").str[0], keys.str.split("|").str[1]
        ok = np.array([comp.at[s, t] >= MIN_CELLS for s, t in zip(spec, state)])
        X, state = X[ok], state[ok].to_numpy()
        lib = np.asarray(X.sum(1)).ravel()
        want = sorted({g for v in MARKERS.values() for g in v})
        cols = [np.where(genes.gene.to_numpy() == g)[0] for g in want]
        present = [(g, c[0]) for g, c in zip(want, cols) if len(c)]
        M = np.asarray(X[:, [c for _, c in present]].todense()) / lib[:, None] * 1e6
        L = pd.DataFrame(np.log2(M + 1), columns=[g for g, _ in present])
        mean = L.groupby(state).mean()
        z = (mean - mean.mean()) / mean.std().replace(0, np.nan)
        z.round(2).to_csv(out_dir / f"markers_{obj}_z.tsv", sep="\t")
        for st, gs in MARKERS.items():
            if st not in z.index:
                continue
            for g in gs:
                if g in z.columns:
                    rows.append(dict(object=obj, state=st, gene=g, z_in_state=z.at[st, g],
                                     peak_state=z[g].idxmax(), n_groups=int((state == st).sum())))
    df = pd.DataFrame(rows)
    df.to_csv(out_dir / "markers_summary.tsv", sep="\t", index=False)
    pd.set_option("display.width", 200)
    print(df.round(2).to_string(index=False))
    s = df.assign(hit=df.peak_state == df.state).groupby(["object", "state"]).hit.agg(["sum", "size"])
    print("\nMarkers peaking in their own state\n", s.to_string())


if __name__ == "__main__":
    main(*sys.argv[1:3])
