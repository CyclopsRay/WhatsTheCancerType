"""Quick checks of the working hypothesis: a polyp's route is written in how it
departs from the same person's normal mucosa.

Pseudobulk only (inputs from build_pseudobulk.py and paired_analysis.py).

  X1 baseline   Does a polyp resemble its own donor's normal more than other
                donors' normals?  (all epithelium, and inside ABS / GOB)
  X2 delta      Do route profiles agree more across donors once each donor's own
                normal is subtracted?  Leave-one-donor-out route calls, raw vs delta.
  X3 newdonors  Score DIS route signatures on VAL polyps, raw vs minus own normal;
                the two-route donor HTA11_6801 shown on its own.
  X4 resemble   Which normal state of the same donor does each lesion state
                (ASC, SSC) resemble most?  A preview of cell matching.
  X5 withinstate  Do the all-epithelium route-specific genes keep their route bias
                inside a fixed state (ABS, GOB, TAC)?

Usage: python hypothesis_checks.py PB_DIR PAIRED_DIR OUT_DIR
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

ROUTES = ["conventional", "serrated"]
N_HVG = 2000
MIN_CELLS = 30
N_TOP = 50


def load(pb_dir, obj):
    spec = pd.read_csv(pb_dir / f"{obj}_specimens.tsv", sep="\t").set_index("HTAN Specimen ID")
    genes = pd.read_csv(pb_dir / f"{obj}_genes.tsv", sep="\t")
    comp = pd.read_csv(pb_dir / f"{obj}_composition.tsv", sep="\t", index_col=0)
    rows = pd.read_csv(pb_dir / f"{obj}_pb_specimen_rows.tsv", sep="\t")["specimen"]
    rows_s = pd.read_csv(pb_dir / f"{obj}_pb_specimen_state_rows.tsv", sep="\t")["specimen_state"]
    sym = genes.set_index("gene_id")["gene"]
    counts = pd.DataFrame(sp.load_npz(pb_dir / f"{obj}_pb_specimen.npz").toarray(),
                          index=rows, columns=genes.gene_id)
    counts_s = pd.DataFrame(sp.load_npz(pb_dir / f"{obj}_pb_specimen_state.npz").toarray(),
                            index=rows_s, columns=genes.gene_id)
    return spec, sym, comp, counts, counts_s


def logcpm(counts):
    lib = counts.sum(1).replace(0, np.nan)
    return np.log2(counts.div(lib, axis=0) * 1e6 + 1)


def hvg(lc, n=N_HVG):
    expr = lc.loc[:, lc.mean(0) > 1]
    return expr.var(0).sort_values(ascending=False).index[:n]


def corr_rows(a, b):
    """Pearson correlation of every row of a with every row of b."""
    az = (a - a.mean(1).values[:, None]) / a.std(1).values[:, None]
    bz = (b - b.mean(1).values[:, None]) / b.std(1).values[:, None]
    return pd.DataFrame(az.values @ bz.values.T / (a.shape[1] - 1), index=a.index, columns=b.index)


def x1_baseline(obj, spec, counts, counts_s):
    """Rank of the own donor's normal among all normals, by similarity to the polyp."""
    out = []
    scopes = [("all", counts, None), ("ABS", counts_s, "ABS"), ("GOB", counts_s, "GOB")]
    for scope, cnt, state in scopes:
        if state:
            cnt = cnt[cnt.index.str.endswith(f"|{state}")]
            cnt = cnt[cnt.sum(1) > 0]
            sid = cnt.index.str.split("|").str[0]
        else:
            sid = cnt.index
        lc = logcpm(cnt)
        lc.index = sid
        # min-cell filter, from the composition table
        ncell = COMPS[obj].sum(1) if not state else COMPS[obj][state]
        keep = [s for s in lc.index if ncell.get(s, 0) >= MIN_CELLS]
        lc = lc.loc[keep]
        meta = spec.loc[lc.index]
        normals = meta.index[meta.route == "normal"]
        lc = lc[hvg(lc.loc[normals])]
        for route in ROUTES:
            polyps = meta.index[meta.route == route]
            c = corr_rows(lc.loc[polyps], lc.loc[normals])
            for p in polyps:
                d = meta.at[p, "donor_id"]
                own = [n for n in normals if meta.at[n, "donor_id"] == d]
                if not own:
                    continue
                donor_best = c.loc[p].groupby(meta.loc[normals, "donor_id"]).max().sort_values(ascending=False)
                rank = int(np.where(donor_best.index == d)[0][0]) + 1
                out.append(dict(object=obj, scope=scope, route=route, polyp=p, donor=d,
                                n_normal_donors=len(donor_best), own_rank=rank,
                                own_r=donor_best[d], best_other_r=donor_best.drop(d).max()))
    return pd.DataFrame(out)


def donor_profiles(spec, lc, route):
    """Per paired donor: mean polyp profile and polyp minus mean own normal."""
    raw, delta = {}, {}
    for d, s in spec.groupby("donor_id"):
        p = s.index[s.route == route].intersection(lc.index)
        n = s.index[s.route == "normal"].intersection(lc.index)
        if len(p) and len(n):
            raw[d] = lc.loc[p].mean()
            delta[d] = lc.loc[p].mean() - lc.loc[n].mean()
    return pd.DataFrame(raw).T, pd.DataFrame(delta).T


def x2_delta(obj, spec, counts):
    lc = logcpm(counts)
    lc = lc.loc[[s for s in lc.index if COMPS[obj].sum(1).get(s, 0) >= MIN_CELLS]]
    lc = lc[hvg(lc)]
    prof = {}
    for route in ROUTES:
        r, dl = donor_profiles(spec, lc, route)
        prof[route] = (r, dl)
    rows, calls = [], []
    for kind, k in [("polyp alone", 0), ("polyp minus own normal", 1)]:
        X = pd.concat([prof["conventional"][k], prof["serrated"][k]])
        y = np.array(["conventional"] * len(prof["conventional"][k]) + ["serrated"] * len(prof["serrated"][k]))
        donors = np.array(list(prof["conventional"][k].index) + list(prof["serrated"][k].index))
        Xc = X - X.mean(0)          # remove the gene mean over all profiles
        C = corr_rows(Xc, Xc).values
        iu = np.triu_indices(len(y), 1)
        same = (y[:, None] == y[None, :])[iu]
        sameperson = (donors[:, None] == donors[None, :])[iu]
        vals = C[iu]
        rows.append(dict(object=obj, profile=kind,
                         within_route_r=vals[same & ~sameperson].mean(),
                         between_route_r=vals[~same & ~sameperson].mean()))
        # leave-one-donor-out nearest centroid on Xc
        correct = 0
        for i, d in enumerate(donors):
            tr = donors != d
            cents = {r: Xc[tr & (y == r)].mean(0) for r in ROUTES}
            sims = {r: np.corrcoef(Xc.iloc[i], cents[r])[0, 1] for r in ROUTES}
            call = max(sims, key=sims.get)
            correct += call == y[i]
            calls.append(dict(object=obj, profile=kind, donor=d, route=y[i], call=call))
        rows[-1].update(n=len(y), loo_correct=int(correct))
    return pd.DataFrame(rows), pd.DataFrame(calls)


def signatures(paired_dir):
    rc = pd.read_csv(paired_dir / "route_compare_DIS_all.tsv", sep="\t", index_col=0)
    sigs = {}
    for name, cat, key in [("conventional_up", "conventional-specific", "log2FoldChange_conv"),
                           ("serrated_up", "serrated-specific", "log2FoldChange_serr")]:
        g = rc[(rc.category == cat) & (rc[key] > 0)]
        sigs[name] = g[key].sort_values(ascending=False).index[:N_TOP].tolist()
    return sigs


def x3_newdonors(spec, counts, comp, sigs):
    """Score DIS signatures on VAL polyps. Score = mean z (over VAL specimens) of signature genes."""
    lc = logcpm(counts)
    lc = lc.loc[[s for s in lc.index if comp.sum(1).get(s, 0) >= MIN_CELLS]]
    z = (lc - lc.mean(0)) / lc.std(0).replace(0, np.nan)
    sc = pd.DataFrame({k: z[[g for g in v if g in z.columns]].mean(1) for k, v in sigs.items()})
    sc["conv_minus_serr"] = sc.conventional_up - sc.serrated_up
    meta = spec.loc[sc.index]
    out = []
    for p in meta.index[meta.route.isin(ROUTES)]:
        d = meta.at[p, "donor_id"]
        own = meta.index[(meta.donor_id == d) & (meta.route == "normal")]
        raw = sc.at[p, "conv_minus_serr"]
        delta = raw - sc.loc[own, "conv_minus_serr"].mean() if len(own) else np.nan
        out.append(dict(polyp=p, donor=d, route=meta.at[p, "route"], type=meta.at[p, "Polyp_Type"],
                        tissue=meta.at[p, "tissue"], has_own_normal=len(own) > 0,
                        conv_score=sc.at[p, "conventional_up"], serr_score=sc.at[p, "serrated_up"],
                        conv_minus_serr_raw=raw, conv_minus_serr_delta=delta,
                        ASC=comp.loc[p, "ASC"] / comp.loc[p].sum(), SSC=comp.loc[p, "SSC"] / comp.loc[p].sum()))
    df = pd.DataFrame(out)
    # threshold 0 on the delta; for raw use the midpoint of the normal specimens' raw score
    thr_raw = sc.loc[meta.index[meta.route == "normal"], "conv_minus_serr"].median()
    df["call_raw"] = np.where(df.conv_minus_serr_raw > thr_raw, "conventional", "serrated")
    df["call_delta"] = np.where(df.conv_minus_serr_delta > 0, "conventional", "serrated")
    case = sc.join(meta[["donor_id", "route", "Polyp_Type"]]).query("donor_id == 'HTA11_6801'")
    return df, case


def x4_resemble(obj, spec, counts_s, comp):
    lc = logcpm(counts_s[counts_s.sum(1) > 0])
    sid = lc.index.str.split("|").str[0]
    st = lc.index.str.split("|").str[1]
    ok = np.array([comp.loc[s, t] >= MIN_CELLS if s in comp.index else False for s, t in zip(sid, st)])
    lc, sid, st = lc[ok], sid[ok], st[ok]
    lc = lc[hvg(lc)]
    out = []
    for lesion, route in [("ASC", "conventional"), ("SSC", "serrated")]:
        for d, s in spec.groupby("donor_id"):
            pol = [i for i in lc.index if i.split("|")[0] in s.index[s.route == route] and i.endswith(f"|{lesion}")]
            nor = [i for i in lc.index if i.split("|")[0] in s.index[s.route == "normal"]
                   and i.split("|")[1] not in ("ASC", "SSC")]
            if not pol or not nor:
                continue
            a = lc.loc[pol].mean().to_frame().T
            b = lc.loc[nor].groupby([i.split("|")[1] for i in nor]).mean()
            c = corr_rows(a, b).iloc[0].sort_values(ascending=False)
            out.append(dict(object=obj, lesion_state=lesion, donor=d, closest=c.index[0],
                            second=c.index[1] if len(c) > 1 else None,
                            **{f"r_{k}": v for k, v in c.items()}))
    return pd.DataFrame(out)


def x5_withinstate(paired_dir):
    out = []
    for obj in ["DIS", "VAL"]:
        allg = pd.read_csv(paired_dir / f"route_compare_{obj}_all.tsv", sep="\t", index_col=0)
        for state in ["ABS", "GOB", "TAC"]:
            rs = pd.read_csv(paired_dir / f"route_compare_{obj}_{state}.tsv", sep="\t", index_col=0)
            for cat, sign in [("conventional-specific", 1), ("serrated-specific", -1)]:
                g = allg.index[allg.category == cat].intersection(rs.index)
                # route bias in the same direction as in all epithelium: |conv| vs |serr| with the gene's sign
                s_all = np.sign(allg.loc[g, "log2FoldChange_conv" if sign > 0 else "log2FoldChange_serr"])
                d = (rs.loc[g, "log2FoldChange_conv"] - rs.loc[g, "log2FoldChange_serr"]) * s_all * sign
                out.append(dict(object=obj, state=state, category=cat, n_genes=len(g),
                                pct_keep_route_bias=100 * (d > 0).mean(),
                                pct_still_route_specific=100 * (rs.loc[g, "category"] == cat).mean()))
    return pd.DataFrame(out)


COMPS = {}


def main(pb_dir, paired_dir, out_dir):
    pb_dir, paired_dir, out_dir = Path(pb_dir), Path(paired_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    data = {o: load(pb_dir, o) for o in ["DIS", "VAL"]}
    for o, (spec, sym, comp, counts, counts_s) in data.items():
        COMPS[o] = comp

    x1 = pd.concat([x1_baseline(o, d[0], d[3], d[4]) for o, d in data.items()])
    x1.to_csv(out_dir / "x1_baseline_ranks.tsv", sep="\t", index=False)
    s1 = x1.groupby(["object", "scope", "route"]).agg(
        n=("polyp", "size"), own_is_closest=("own_rank", lambda r: int((r == 1).sum())),
        median_rank=("own_rank", "median"), median_n_donors=("n_normal_donors", "median"),
        expected_closest=("n_normal_donors", lambda n: (1 / n).sum())).reset_index()
    s1.to_csv(out_dir / "x1_baseline_summary.tsv", sep="\t", index=False)
    print("X1 own-normal rank\n", s1.round(2).to_string(index=False))

    x2 = [x2_delta(o, d[0], d[3]) for o, d in data.items()]
    s2 = pd.concat([a for a, _ in x2])
    pd.concat([b for _, b in x2]).to_csv(out_dir / "x2_loo_calls.tsv", sep="\t", index=False)
    s2.to_csv(out_dir / "x2_delta_summary.tsv", sep="\t", index=False)
    print("\nX2 raw vs delta\n", s2.round(3).to_string(index=False))

    sigs = signatures(paired_dir)
    spec, sym, comp, counts, counts_s = data["VAL"]
    x3, case = x3_newdonors(spec, counts, comp, sigs)
    x3.to_csv(out_dir / "x3_val_route_calls.tsv", sep="\t", index=False)
    case.to_csv(out_dir / "x3_HTA11_6801.tsv", sep="\t")
    paired = x3[x3.has_own_normal]
    print("\nX3 VAL polyps, DIS signatures")
    for k in ["call_raw", "call_delta"]:
        print(f"  {k}: all {int((x3[k] == x3.route).sum())}/{len(x3)}; "
              f"paired {int((paired[k] == paired.route).sum())}/{len(paired)}")
    print(x3.round(2).to_string(index=False))
    print("\nHTA11_6801\n", case.round(2).to_string())

    x4 = pd.concat([x4_resemble(o, d[0], d[4], d[2]) for o, d in data.items()])
    x4.to_csv(out_dir / "x4_resemblance.tsv", sep="\t", index=False)
    print("\nX4 closest normal state of the same donor\n",
          x4.groupby(["object", "lesion_state"]).closest.value_counts().to_string())
    print(x4.groupby(["lesion_state"])[[c for c in x4.columns if c.startswith("r_")]].median().round(3).to_string())

    x5 = x5_withinstate(paired_dir)
    x5.to_csv(out_dir / "x5_withinstate.tsv", sep="\t", index=False)
    print("\nX5 route bias inside a fixed state\n", x5.round(1).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])
