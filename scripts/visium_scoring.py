"""Score scRNA-derived polyp signatures on the OSF Visium polyp captures.

Signatures come from the DIS paired DE (route_compare_DIS_all.tsv): genes up in
polyp that are shared by both routes, conventional-specific, or serrated-specific.
Each capture's raw counts are log-normalized and scored with scanpy.tl.score_genes;
scores are summarised per pathologist spot annotation, and adenoma spots are
compared with normal_mucosa spots on the same section where both exist.

Usage: python visium_scoring.py ST_DIR PAIRED_DIR OUT_DIR
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scanpy as sc
from scipy.stats import mannwhitneyu

N_TOP = 50
ROUTE_OF = {"TA/TVA": "conventional", "SSL/HP": "serrated"}


def signatures(paired_dir):
    rc = pd.read_csv(paired_dir / "route_compare_DIS_all.tsv", sep="\t", index_col=0)
    up = lambda col: rc[col] > 0
    sigs = {}
    for name, mask, key in [
        ("shared_up", (rc.category == "shared") & up("log2FoldChange_conv"), "log2FoldChange_conv"),
        ("conventional_up", (rc.category == "conventional-specific") & up("log2FoldChange_conv"), "log2FoldChange_conv"),
        ("serrated_up", (rc.category == "serrated-specific") & up("log2FoldChange_serr"), "log2FoldChange_serr"),
        ("shared_down", (rc.category == "shared") & ~up("log2FoldChange_conv"), "log2FoldChange_conv"),
    ]:
        g = rc[mask].reindex(rc[mask][key].abs().sort_values(ascending=False).index)
        sigs[name] = g.gene.dropna().drop_duplicates().head(N_TOP).tolist()
    return sigs


def main(st_dir, paired_dir, out_dir):
    st_dir, paired_dir, out_dir = Path(st_dir), Path(paired_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sigs = signatures(paired_dir)
    pd.Series({k: ",".join(v) for k, v in sigs.items()}).to_csv(out_dir / "signatures.tsv", sep="\t", header=False)
    summary, tests = [], []
    for f in sorted(st_dir.glob("*_master.h5ad")):
        ad = sc.read_h5ad(f)
        ad.var_names_make_unique()
        sc.pp.normalize_total(ad, target_sum=1e4)
        sc.pp.log1p(ad)
        cap = f.name.replace("_master.h5ad", "")
        ttype = ad.obs["Tumor Type"].astype(str).iloc[0]
        for name, genes in sigs.items():
            present = [g for g in genes if g in ad.var_names]
            sc.tl.score_genes(ad, present, score_name=name, random_state=0)
        keep = ["pathology_annotation", "array_row", "array_col"] + list(sigs) + \
               [c for c in ["ASC_VUMCrefNMF30", "SSC_VUMCrefNMF30", "STM_VUMCrefNMF30"] if c in ad.obs]
        spots = ad.obs[keep].copy()
        spots[["x", "y"]] = ad.obsm["spatial"][:, :2]
        spots.assign(capture=cap, tumor_type=ttype).to_csv(out_dir / f"spots_{cap}.tsv.gz", sep="\t")
        g = spots.groupby("pathology_annotation")[list(sigs)].mean()
        g["n_spots"] = spots.pathology_annotation.value_counts()
        summary.append(g.assign(capture=cap, tumor_type=ttype).reset_index())
        ann = spots.pathology_annotation.astype(str)
        lesion = ann.isin(["adenoma", "SSL", "HP", "polyp"]) | ann.str.contains("adenoma$|ssl|serrated", case=False)
        normal = ann.eq("normal_mucosa")
        for name in sigs:
            a, b = spots.loc[lesion, name], spots.loc[normal, name]
            row = dict(capture=cap, tumor_type=ttype, signature=name, n_lesion=len(a), n_normal=len(b),
                       mean_lesion=a.mean(), mean_normal=b.mean())
            if len(a) >= 10 and len(b) >= 10:
                row["mwu_p"] = mannwhitneyu(a, b).pvalue
                row["auc"] = mannwhitneyu(a, b).statistic / (len(a) * len(b))
            tests.append(row)
        print(cap, ttype, dict(ann.value_counts()), flush=True)
    pd.concat(summary).to_csv(out_dir / "score_by_annotation.tsv", sep="\t", index=False)
    pd.DataFrame(tests).to_csv(out_dir / "lesion_vs_normal_spots.tsv", sep="\t", index=False)
    print(pd.DataFrame(tests).round(3).to_string(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
