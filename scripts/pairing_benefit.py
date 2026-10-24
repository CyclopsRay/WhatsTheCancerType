"""X6: does anchoring each polyp to its own donor help?

Refits the all-epithelium polyp-vs-normal DESeq2 per object and route on the same
specimens as paired_analysis.py, once with ~ donor + condition (paired) and once
with ~ condition (unpaired), then compares hit counts and DIS -> VAL replication.

Usage: python pairing_benefit.py PB_DIR OUT_DIR N_CPUS
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
from pydeseq2.default_inference import DefaultInference

sys.path.insert(0, str(Path(__file__).parent))
from paired_analysis import load, paired_donors, ROUTES, PADJ, LFC, MIN_CELLS  # noqa: E402


def fit(counts, meta, design, n_cpus):
    keep = (counts >= 10).sum(0) >= 3
    counts = counts.loc[:, keep].round().astype(int)
    inf = DefaultInference(n_cpus=n_cpus)
    dds = DeseqDataSet(counts=counts, metadata=meta, design=design,
                       refit_cooks=True, inference=inf, quiet=True)
    dds.deseq2()
    ds = DeseqStats(dds, contrast=["condition", "polyp", "normal"], inference=inf, quiet=True)
    ds.summary()
    return ds.results_df


def hits(res):
    return res.index[(res.padj < PADJ) & (res.log2FoldChange.abs() > LFC)]


def main(pb_dir, out_dir, n_cpus):
    pb_dir, out_dir, n_cpus = Path(pb_dir), Path(out_dir), int(n_cpus)
    out_dir.mkdir(parents=True, exist_ok=True)
    res = {}
    for obj in ["DIS", "VAL"]:
        spec, genes, comp, counts, counts_s = load(pb_dir, obj)
        for route in ROUTES:
            # same specimen selection as paired_analysis.de_fit, scope "all"
            donors = paired_donors(spec, route)
            s = spec[spec.donor_id.isin(donors) & spec.route.isin(["normal", route])]
            s = s[s.n_cells >= MIN_CELLS]
            ok = s.groupby("donor_id")["route"].agg(lambda r: {"normal", route} <= set(r))
            s = s[s.donor_id.isin(ok[ok].index)]
            meta = pd.DataFrame({"donor": s.donor_id.values,
                                 "condition": np.where(s.route == "normal", "normal", "polyp")},
                                index=s.index)
            X = counts.loc[s.index]
            for name, design in [("paired", "~donor + condition"), ("unpaired", "~condition")]:
                r = fit(X, meta, design, n_cpus)
                r.to_csv(out_dir / f"x6_de_{obj}_{route}_{name}.tsv", sep="\t")
                res[(obj, route, name)] = r
                print(obj, route, name, "specimens", len(meta), "hits", len(hits(r)), flush=True)
    rows = []
    for route in ROUTES:
        for name in ["paired", "unpaired"]:
            d, v = res[("DIS", route, name)], res[("VAL", route, name)]
            h = hits(d).intersection(v.index)
            same = np.sign(d.loc[h, "log2FoldChange"]) == np.sign(v.loc[h, "log2FoldChange"])
            vsig = v.loc[h, "padj"] < PADJ
            rows.append(dict(route=route, model=name, DIS_hits=len(hits(d)), VAL_hits=len(hits(v)),
                             DIS_hits_tested_in_VAL=len(h), pct_same_sign=100 * same.mean(),
                             pct_also_sig_VAL=100 * (same & vsig).mean(),
                             median_DIS_lfcSE=d.lfcSE.median()))
    summ = pd.DataFrame(rows)
    summ.to_csv(out_dir / "x6_pairing_summary.tsv", sep="\t", index=False)
    print(summ.round(2).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])
