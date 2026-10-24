"""Build the interactive "pick a person" page for the talk.

Packs our label-free UMAP (derived/label_free/{DIS,VAL}_embedding.tsv.gz) into a single HTML
page: coordinates quantised to 0..4095 (uint16), person and tissue codes (uint8), base64-encoded.
Per person it also carries the median share of same-person neighbours (healthy vs polyp cells) and
the X1 rank of each polyp's own healthy lining among all candidates
(derived/hypothesis/x1_baseline_ranks.tsv, scope "all").

Usage: python make_person_explorer.py DERIVED_DIR TEMPLATE_HTML OUT_HTML
"""
import base64
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROUTE_CODE = {"normal": 0, "conventional": 1, "serrated": 2}
COHORT_NAME = {"DIS": "First group of people", "VAL": "Second group of people"}


def pack(arr, dtype):
    return base64.b64encode(np.ascontiguousarray(arr, dtype=dtype).tobytes()).decode()


def main(derived, template, out):
    derived = Path(derived)
    x1 = pd.read_csv(derived / "hypothesis" / "x1_baseline_ranks.tsv", sep="\t")
    x1 = x1[x1.scope == "all"]
    cohorts = []
    for obj in ["DIS", "VAL"]:
        d = pd.read_csv(derived / "label_free" / f"{obj}_embedding.tsv.gz", sep="\t")
        d = d.sample(frac=1, random_state=0)
        q = lambda v: np.round((v - v.min()) / (v.max() - v.min()) * 4095)
        donors = sorted(d.donor_id.unique(), key=lambda s: int(s.split("_")[1]))
        code = {p: i for i, p in enumerate(donors)}
        people = []
        for p in donors:
            s = d[d.donor_id == p]
            routes = [r for r in ["conventional", "serrated"] if (s.route == r).any()]
            h, pol = s[s.route == "normal"], s[s.route != "normal"]
            ranks = [dict(route=r.route, rank=int(r.own_rank), of=int(r.n_normal_donors))
                     for r in x1[(x1.object == obj) & (x1.donor == p)].itertuples()]
            people.append(dict(id=p, routes=routes, healthy=len(h), polyp=len(pol),
                               nbrHealthy=round(float(h.nbr_same_donor.median()), 2) if len(h) else None,
                               nbrPolyp=round(float(pol.nbr_same_donor.median()), 2) if len(pol) else None,
                               ranks=ranks))
        cohorts.append(dict(key=obj, name=COHORT_NAME[obj], n=len(d),
                            x=pack(q(d.umap1), "<u2"), y=pack(4095 - q(d.umap2), "<u2"),
                            person=pack(d.donor_id.map(code), "u1"),
                            tissue=pack(d.route.map(ROUTE_CODE), "u1"), people=people))
    html = Path(template).read_text().replace("/*__DATA__*/null", json.dumps(cohorts, separators=(",", ":")))
    Path(out).write_text(html)
    print(out, round(len(html) / 1e6, 2), "MB")


if __name__ == "__main__":
    main(*sys.argv[1:4])
