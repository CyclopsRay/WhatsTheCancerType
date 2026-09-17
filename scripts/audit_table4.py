#!/usr/bin/env python3
"""Recount Supplementary Table 4; this is a metadata audit, not a sequencing reanalysis."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from inspect_paper_supplements import xlsx_sheets

PROJECT = Path(__file__).resolve().parents[1]


def numeric(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def mutation_counts(rows, column):
    values = [numeric(row.get(column)) for row in rows]
    values = [value for value in values if value is not None]
    positive = sum(value >= 3 for value in values)
    return {"n_with_count": len(values), "n_at_least_3": positive,
            "percent_at_least_3": 100 * positive / len(values) if values else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path,
                        default=PROJECT / "record/001_temporal_recording/sources/table4.xlsx")
    parser.add_argument("--output", type=Path, help="Create a new JSON result; refuses to overwrite")
    args = parser.parse_args()
    sheets = dict(xlsx_sheets(args.path))
    expected = {"HTAN_Vanderbilt": ("A", "SPECID"),
                "WES_human_polyps": ("F", "APC_mut_count"),
                "scRNAseq_human_polyps": ("G", "Median_VAF"),
                "TCPS_Human_APC_count": ("B", "#APC_mut")}
    for name, (column, value) in expected.items():
        if sheets[name][0]["values"].get(column) != value:
            raise ValueError(f"Unexpected header in {name}; inspect the source before counting")
    cohort = [r["values"] for r in sheets["HTAN_Vanderbilt"][1:]]
    wes = [r["values"] for r in sheets["WES_human_polyps"][1:]]
    scrna = [r["values"] for r in sheets["scRNAseq_human_polyps"][1:]]
    targeted = [r["values"] for r in sheets["TCPS_Human_APC_count"][1:]]
    mouse_sheet = sheets["Mouse_tumor_analysis"]
    if mouse_sheet[1]["values"].get("F") != "Number_of_Apc_Mut":
        raise ValueError("Unexpected mouse WES header")
    # Only the first table is WES specimens; later tables contain mutation-level rows.
    mouse = []
    for row in mouse_sheet[2:]:
        if numeric(row["values"].get("F")) is None:
            break
        mouse.append(row["values"])
    result = {
        "source": str(args.path.resolve()),
        "source_sha256": hashlib.sha256(args.path.read_bytes()).hexdigest(),
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "cohort": {"rows": len(cohort),
                   "unique_participant_ids": len({r["B"] for r in cohort}),
                   "sample_types": dict(Counter(r.get("I", "<empty>") for r in cohort))},
        "human_wes": {"rows": len(wes),
                      "sample_types": dict(Counter(r.get("E", "<empty>") for r in wes)),
                      "apc": mutation_counts(wes, "F")},
        "tcps": {"rows": len(targeted), "apc": mutation_counts(targeted, "B")},
        "scrna_analysis_sheet": {
            "rows": len(scrna),
            "unique_specimen_ids": len({r["B"] for r in scrna if "B" in r}),
            "rows_with_numeric_median_vaf": sum(numeric(r.get("G")) is not None for r in scrna),
            "note": "Analysis-sheet rows are not automatically unique cohort specimens."},
        "mouse_wes": {"rows": len(mouse), "apc": mutation_counts(mouse, "F")},
        "scope": "Counts from supplied metadata; no raw reads or variant calls reprocessed.",
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as output:
            output.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()
