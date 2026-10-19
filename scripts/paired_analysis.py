"""Within-donor polyp vs matched normal analysis, per route, in DIS and VAL.

Inputs are the tables written by build_pseudobulk.py. Replication unit is the
donor: only donors with both a normal specimen and a polyp of the route enter a
fit, and the DESeq2 design is ~ donor + condition (paired).

Outputs (OUT_DIR):
  composition_paired.tsv      per object x route x state: donor-level deltas
  de_{OBJ}_{route}_{scope}.tsv PyDESeq2 results (scope = all epithelium or a state)
  route_compare_{OBJ}_{scope}.tsv  conventional vs serrated effects + difference test
  replication_summary.tsv     DIS-significant genes re-tested in VAL
  donor_consistency_{OBJ}_{route}.tsv  per-gene count of donors agreeing in sign
  gsea_{OBJ}_{route}_all.tsv  Hallmark prerank on the Wald statistic

Usage: python paired_analysis.py PB_DIR GMT OUT_DIR N_CPUS
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.stats import wilcoxon, spearmanr, norm
from statsmodels.stats.multitest import multipletests
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
from pydeseq2.default_inference import DefaultInference

warnings.filterwarnings("ignore")
ROUTES = ["conventional", "serrated"]
STATES_DE = ["ABS", "GOB", "TAC"]   # states present in both normal and polyp
MIN_CELLS = 30                       # per specimen (or specimen x state) pseudobulk
PADJ, LFC = 0.05, 1.0


def load(pb_dir, obj):
    spec = pd.read_csv(pb_dir / f"{obj}_specimens.tsv", sep="\t").set_index("HTAN Specimen ID")
    genes = pd.read_csv(pb_dir / f"{obj}_genes.tsv", sep="\t")
    comp = pd.read_csv(pb_dir / f"{obj}_composition.tsv", sep="\t", index_col=0)
    pb = sp.load_npz(pb_dir / f"{obj}_pb_specimen.npz").toarray()
    rows = pd.read_csv(pb_dir / f"{obj}_pb_specimen_rows.tsv", sep="\t")["specimen"]
    pbs = sp.load_npz(pb_dir / f"{obj}_pb_specimen_state.npz").toarray()
    rows_s = pd.read_csv(pb_dir / f"{obj}_pb_specimen_state_rows.tsv", sep="\t")["specimen_state"]
    counts = pd.DataFrame(pb, index=rows, columns=genes.gene_id)
    counts_s = pd.DataFrame(pbs, index=rows_s, columns=genes.gene_id)
    return spec, genes, comp, counts, counts_s


def paired_donors(spec, route):
    by = spec.groupby("donor_id")["route"].agg(set)
    return sorted(d for d, r in by.items() if "normal" in r and route in r)


def composition(obj, spec, comp):
    frac = comp.div(comp.sum(1), axis=0)
    out = []
    for route in ROUTES:
        donors = paired_donors(spec, route)
        for state in frac.columns:
            deltas = []
            for d in donors:
                s = spec[spec.donor_id == d]
                p = frac.loc[s.index[s.route == route], state].mean()
                n = frac.loc[s.index[s.route == "normal"], state].mean()
                deltas.append(p - n)
            deltas = np.array(deltas)
            p = wilcoxon(deltas).pvalue if np.any(deltas != 0) else 1.0
            out.append(dict(object=obj, route=route, state=state, n_donors=len(donors),
                            median_delta_pct=100 * np.median(deltas),
                            donors_up=int((deltas > 0).sum()), donors_down=int((deltas < 0).sum()),
                            wilcoxon_p=p))
    df = pd.DataFrame(out)
    df["padj"] = multipletests(df.wilcoxon_p, method="fdr_bh")[1]
    return df


def run_deseq(counts, meta, n_cpus):
    keep = (counts >= 10).sum(0) >= 3
    counts = counts.loc[:, keep].round().astype(int)
    inf = DefaultInference(n_cpus=n_cpus)
    dds = DeseqDataSet(counts=counts, metadata=meta, design="~donor + condition",
                       refit_cooks=True, inference=inf, quiet=True)
    dds.deseq2()
    ds = DeseqStats(dds, contrast=["condition", "polyp", "normal"], inference=inf, quiet=True)
    ds.summary()
    return ds.results_df


def de_fit(spec, counts, route, scope, n_cpus, counts_s=None, comp=None):
    donors = paired_donors(spec, route)
    s = spec[spec.donor_id.isin(donors) & spec.route.isin(["normal", route])].copy()
    if scope == "all":
        s = s[s.n_cells >= MIN_CELLS]
        X = counts.loc[s.index]
    else:
        s = s[comp.reindex(s.index)[scope].fillna(0) >= MIN_CELLS]
        X = counts_s.loc[[f"{i}|{scope}" for i in s.index]]
        X.index = s.index
    # keep donors that still have both conditions after the cell filter
    ok = s.groupby("donor_id")["route"].agg(lambda r: {"normal", route} <= set(r))
    s = s[s.donor_id.isin(ok[ok].index)]
    meta = pd.DataFrame({"donor": s.donor_id.values,
                         "condition": np.where(s.route == "normal", "normal", "polyp")},
                        index=s.index)
    res = run_deseq(X.loc[s.index], meta, n_cpus)
    return res, meta, X.loc[s.index]


def donor_consistency(res, meta, X, genes_sig):
    cpm = np.log2(X.div(X.sum(1), axis=0) * 1e6 + 1)
    rows = []
    for d, g in meta.groupby("donor"):
        p = cpm.loc[g.index[g.condition == "polyp"]].mean()
        n = cpm.loc[g.index[g.condition == "normal"]].mean()
        rows.append((p - n).rename(d))
    delta = pd.concat(rows, axis=1).loc[genes_sig]
    sign = np.sign(res.loc[genes_sig, "log2FoldChange"])
    agree = (np.sign(delta).mul(sign, axis=0) > 0).sum(1)
    return pd.DataFrame({"log2FoldChange": res.loc[genes_sig, "log2FoldChange"],
                         "donors_agree": agree, "n_donors": delta.shape[1]})


def sig(res):
    return res.index[(res.padj < PADJ) & (res.log2FoldChange.abs() > LFC)]


def route_compare(rc, rs, genes):
    j = rc[["log2FoldChange", "lfcSE", "padj"]].join(
        rs[["log2FoldChange", "lfcSE", "padj"]], lsuffix="_conv", rsuffix="_serr", how="inner")
    z = (j.log2FoldChange_conv - j.log2FoldChange_serr) / np.sqrt(j.lfcSE_conv**2 + j.lfcSE_serr**2)
    j["diff_z"] = z
    j["diff_padj"] = multipletests(np.nan_to_num(2 * norm.sf(np.abs(z)), nan=1), method="fdr_bh")[1]
    sc = (j.padj_conv < PADJ) & (j.log2FoldChange_conv.abs() > LFC)
    ss = (j.padj_serr < PADJ) & (j.log2FoldChange_serr.abs() > LFC)
    same = np.sign(j.log2FoldChange_conv) == np.sign(j.log2FoldChange_serr)
    cat = np.select([sc & ss & same, sc & ss & ~same,
                     sc & ~ss & (j.diff_padj < PADJ), ss & ~sc & (j.diff_padj < PADJ),
                     sc | ss], ["shared", "opposite", "conventional-specific",
                                "serrated-specific", "one route, difference not significant"],
                    "not significant")
    j["category"] = cat
    return j.join(genes.set_index("gene_id")["gene"])


def gsea(res, genes, gmt, out):
    import gseapy
    rnk = res.dropna(subset=["stat", "gene"])
    rnk = rnk.groupby("gene")["stat"].mean().sort_values(ascending=False)
    pre = gseapy.prerank(rnk=rnk, gene_sets=str(gmt), permutation_num=1000, min_size=15,
                         max_size=500, seed=0, threads=4, outdir=None, verbose=False)
    pre.res2d.to_csv(out, sep="\t", index=False)


def main(pb_dir, gmt, out_dir, n_cpus):
    pb_dir, out_dir = Path(pb_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {o: load(pb_dir, o) for o in ["DIS", "VAL"]}
    comps, summary, results = [], [], {}
    for obj, (spec, genes, comp, counts, counts_s) in data.items():
        comps.append(composition(obj, spec, comp))
        for scope in ["all"] + STATES_DE:
            for route in ROUTES:
                res, meta, X = de_fit(spec, counts, route, scope, n_cpus, counts_s, comp)
                res = res.join(genes.set_index("gene_id")["gene"])
                res.to_csv(out_dir / f"de_{obj}_{route}_{scope}.tsv", sep="\t")
                results[(obj, route, scope)] = res
                s = sig(res)
                summary.append(dict(object=obj, route=route, scope=scope,
                                    n_donors=meta.donor.nunique(), n_specimens=len(meta),
                                    genes_tested=int(res.padj.notna().sum()), sig_up=int((res.loc[s].log2FoldChange > 0).sum()),
                                    sig_down=int((res.loc[s].log2FoldChange < 0).sum())))
                print(summary[-1], flush=True)
                if scope == "all":
                    donor_consistency(res, meta, X, s).to_csv(
                        out_dir / f"donor_consistency_{obj}_{route}.tsv", sep="\t")
                    gsea(res, genes, gmt, out_dir / f"gsea_{obj}_{route}_all.tsv")
            rc = route_compare(results[(obj, "conventional", scope)],
                               results[(obj, "serrated", scope)], genes)
            rc.to_csv(out_dir / f"route_compare_{obj}_{scope}.tsv", sep="\t")
    pd.concat(comps).to_csv(out_dir / "composition_paired.tsv", sep="\t", index=False)
    pd.DataFrame(summary).to_csv(out_dir / "de_summary.tsv", sep="\t", index=False)

    replicate(out_dir)


def replicate(out_dir):
    """DIS-significant genes re-tested in VAL, from the saved DE tables."""
    out_dir = Path(out_dir)
    rep = []
    for scope in ["all"] + STATES_DE:
        for route in ROUTES:
            d = pd.read_csv(out_dir / f"de_DIS_{route}_{scope}.tsv", sep="\t", index_col=0)
            v = pd.read_csv(out_dir / f"de_VAL_{route}_{scope}.tsv", sep="\t", index_col=0)
            s = sig(d).intersection(v.index)
            both = d.index.intersection(v.index)
            rho = spearmanr(d.loc[both, "log2FoldChange"], v.loc[both, "log2FoldChange"], nan_policy="omit")[0]
            same = np.sign(d.loc[s, "log2FoldChange"]) == np.sign(v.loc[s, "log2FoldChange"])
            rep.append(dict(route=route, scope=scope, dis_sig=len(sig(d)), dis_sig_tested_in_val=len(s),
                            sign_agree_frac=same.mean(),
                            val_padj05_same_sign=int(((v.loc[s, "padj"] < PADJ) & same).sum()),
                            spearman_lfc_all_genes=rho))
    rep = pd.DataFrame(rep)
    rep.to_csv(out_dir / "replication_summary.tsv", sep="\t", index=False)
    print(rep.to_string(), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--replicate":
        replicate(sys.argv[2])
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
