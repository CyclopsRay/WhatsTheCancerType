#!/usr/bin/env python3
"""Inventory Stanford GEO/ENA files or probe a bounded batch with two-byte GETs.

Inputs are public GSE201349 family SOFT and PRJNA830914/PRJNA830903 ENA TSVs.
Network work is bounded curl I/O (one to three connections per batch).
No sequencing analysis or full data download.
"""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import re
import subprocess


def file_accessible(check):
    """Reject directory/error bodies and raw exports with unexpected total size."""
    ranges = check.get("content_range", [])
    match = re.fullmatch(r"bytes 0-1/(\d+)", ranges[0]) if ranges else None
    if not check["range_accessible"] or not match:
        return False
    if "text/html" in (check.get("content_type") or "").lower():
        return False
    return "bytes" not in check or int(match.group(1)) == check["bytes"]


def inventory(soft, ena_paths):
    samples = {}
    current = None
    with gzip.open(soft, "rt") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("^"):
                current = None
                if line.startswith("^SAMPLE = "):
                    current = line.split(" = ", 1)[1]
                    samples[current] = {"gsm": current, "files": [], "srx": ""}
            elif current and " = " in line:
                key, value = line.split(" = ", 1)
                sample = samples[current]
                if key == "!Sample_title":
                    sample["title"] = value
                elif key == "!Sample_library_strategy":
                    sample["assay"] = value
                elif key.startswith("!Sample_supplementary_file") and value.startswith("ftp://"):
                    sample["files"].append(value.replace("ftp://", "https://", 1))
                elif key == "!Sample_relation" and "SRX" in value:
                    sample["srx"] = re.search(r"SRX\d+", value).group()
    files = []
    for sample in samples.values():
        for url in sample["files"]:
            files.append({"kind": "processed", "assay": sample["assay"],
                          "gsm": sample["gsm"], "srx": sample["srx"], "url": url})
    by_srx = {s["srx"]: s for s in samples.values()}
    runs = []
    for path in ena_paths:
        with path.open() as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                if row["experiment_accession"] not in by_srx:
                    raise ValueError(f"ENA experiment absent from GEO: {row['experiment_accession']}")
                runs.append(row)
                sample = by_srx[row["experiment_accession"]]
                urls = row["fastq_ftp"].split(";") if row["fastq_ftp"] else []
                sizes = row["fastq_bytes"].split(";") if row["fastq_bytes"] else []
                if len(urls) != len(sizes):
                    raise ValueError("ENA URL/size count mismatch")
                for url, size in zip(urls, sizes):
                    files.append({"kind": "raw_fastq", "assay": sample["assay"],
                                  "gsm": sample["gsm"], "srx": sample["srx"],
                                  "run": row["run_accession"], "bytes": int(size),
                                  "url": "https://" + url})
    return {"generated_utc": datetime.now(timezone.utc).isoformat(),
            "samples": list(samples.values()), "runs": runs, "files": files}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    build = sub.add_parser("inventory")
    build.add_argument("--soft", type=Path, required=True)
    build.add_argument("--ena", type=Path, nargs="+", required=True)
    build.add_argument("--output", type=Path, required=True)
    probe = sub.add_parser("probe")
    probe.add_argument("--manifest", type=Path, required=True)
    probe.add_argument("--start", type=int, default=0)
    probe.add_argument("--limit", type=int, default=50)
    probe.add_argument("--indices", type=int, nargs="+",
                       help="Explicit manifest indices for a bounded retry batch")
    probe.add_argument("--timeout", type=int, choices=(12, 30), default=12)
    probe.add_argument("--output", type=Path, required=True)
    probe.add_argument("--connections", type=int, choices=(1, 2, 3), default=1,
                       help="Concurrent curl transfers (network I/O only; no Python workers)")
    summary = sub.add_parser("summarize")
    summary.add_argument("--manifest", type=Path, required=True)
    summary.add_argument("--checks", type=Path, nargs="+", required=True)
    summary.add_argument("--rechecks", type=Path, nargs="*", default=[],
                         help="Optional later attempts; last supplied attempt per file is used")
    summary.add_argument("--metadata", type=Path, required=True)
    summary.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; use a new filename to preserve previous evidence")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.mode == "summarize":
        from inspect_paper_supplements import xlsx_sheets
        manifest = json.loads(args.manifest.read_text())
        checks = [json.loads(line) for path in args.checks for line in path.read_text().splitlines()]
        indices = [c["file_index"] for c in checks]
        if len(indices) != len(set(indices)):
            raise ValueError("Duplicate file indices; select one attempt per file")
        if set(indices) != set(range(len(manifest["files"]))):
            raise ValueError("Not every manifest file has a check")
        initial_bytes = sum(c["bytes_downloaded"] for c in checks)
        initial_passed = sum(c["range_accessible"] for c in checks)
        retries = [json.loads(line) for path in args.rechecks for line in path.read_text().splitlines()]
        by_index = {c["file_index"]: c for c in checks}
        for check in retries:
            index = check["file_index"]
            if index not in by_index or check["url"] != manifest["files"][index]["url"]:
                raise ValueError("Recheck URL/index does not match manifest")
            by_index[index] = check
        checks = [by_index[i] for i in sorted(by_index)]
        for check in checks:
            if check["url"] != manifest["files"][check["file_index"]]["url"]:
                raise ValueError("Check URL does not match manifest index")
        groups = []
        for kind, assay in sorted({(c["kind"], c["assay"]) for c in checks}):
            group = [c for c in checks if c["kind"] == kind and c["assay"] == assay]
            total_bytes = 0
            for check in group:
                ranges = check["content_range"]
                if ranges and re.search(r"/\d+$", ranges[0]):
                    total_bytes += int(ranges[0].rsplit("/", 1)[1])
            groups.append({"kind": kind, "assay": assay, "files": len(group),
                           "libraries": len({c["gsm"] for c in group}),
                           "range_passed": sum(c["range_accessible"] for c in group),
                           "file_access_passed": sum(file_accessible(c) for c in group),
                           "unverified_file_indices": [c["file_index"] for c in group if not file_accessible(c)],
                           "file_bytes_from_content_range": total_bytes})
        sheets = dict(xlsx_sheets(args.metadata))
        titles = {s["title"] for s in manifest["samples"]}
        mappings = []
        for sheet, column in [("TableS3", "E"), ("TableS3", "F"), ("TableS4", "E"), ("TableS5", "D")]:
            values = {r["values"].get(column, "").strip() for r in sheets[sheet][1:]} - {"", "NA"}
            mappings.append({"sheet": sheet, "column": column, "unique_titles": len(values),
                             "missing_from_geo": sorted(values - titles)})
        result = {"generated_utc": datetime.now(timezone.utc).isoformat(),
                  "manifest_files": len(manifest["files"]), "checked_files": len(checks),
                  "initial_range_passed": initial_passed,
                  "recheck_attempts": len(retries),
                  "total_bytes_transferred": initial_bytes + sum(c["bytes_downloaded"] for c in retries),
                  "groups": groups, "supplementary_metadata_mappings": mappings,
                  "scope": "Anonymous two-byte GET access, not whole-file integrity or barcode-read completeness; WGS not verified."}
        with args.output.open("x") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
        print(json.dumps(result, indent=2))
        return
    if args.mode == "inventory":
        result = inventory(args.soft, args.ena)
        with args.output.open("x") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
        print("Samples:", dict(Counter(s["assay"] for s in result["samples"])))
        print("Files:", dict(Counter((s["kind"], s["assay"]) for s in result["files"])))
        print("Runs:", len(result["runs"]))
        return
    if args.start < 0 or not 1 <= args.limit <= 100:
        parser.error("Require start >= 0 and 1 <= limit <= 100")
    all_files = json.loads(args.manifest.read_text())["files"]
    indices = args.indices if args.indices is not None else list(
        range(args.start, min(args.start + args.limit, len(all_files))))
    if (len(indices) > 100 or len(indices) != len(set(indices))
            or any(i < 0 or i >= len(all_files) for i in indices)):
        parser.error("Require at most 100 unique valid manifest indices")
    files = [all_files[i] for i in indices]
    if not files:
        parser.error("Empty selected batch")
    command = ["curl", "--silent", "--show-error", "--location", "--range", "0-1",
               "--max-filesize", "4096", "--max-time", str(args.timeout), "--connect-timeout", "5",
               "--write-out", '{"transfer":%{json},"headers":%{header_json}}\n']
    if args.connections > 1:
        command.extend(["--parallel", "--parallel-max", str(args.connections)])
    for entry in files:
        command.extend(["--url", entry["url"], "--output", "/dev/null"])
    checked = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, capture_output=True, text=True)
    # curl header_json contains embedded newlines; decode whole JSON objects.
    transfers = []
    remaining = result.stdout.lstrip()
    decoder = json.JSONDecoder()
    while remaining:
        value, end = decoder.raw_decode(remaining)
        transfers.append(value)
        remaining = remaining[end:].lstrip()
    if len(transfers) != len(files):
        raise RuntimeError(f"Expected {len(files)} transfers, received {len(transfers)}; {result.stderr[:300]}")
    transfers.sort(key=lambda response: response["transfer"]["urlnum"])
    if [r["transfer"]["urlnum"] for r in transfers] != list(range(len(files))):
        raise RuntimeError("Missing or duplicate curl transfer indices")
    counts = Counter()
    with args.output.open("x") as handle:
        for index, entry, response in zip(indices, files, transfers):
            transfer = response["transfer"]
            passed = (transfer["http_code"] == 206 and transfer["exitcode"] == 0
                      and transfer["size_download"] == 2)
            record = {"file_index": index, "checked_utc": checked, **entry,
                      "range_accessible": passed, "http_code": transfer["http_code"],
                      "exitcode": transfer["exitcode"], "bytes_downloaded": transfer["size_download"],
                      "effective_url": transfer["url_effective"],
                      "content_range": response["headers"].get("content-range", []),
                      "content_type": transfer.get("content_type"),
                      "error": transfer.get("errormsg")}
            handle.write(json.dumps(record) + "\n")
            counts[(entry["kind"], entry["assay"], passed, transfer["http_code"]) ] += 1
    print(f"Checked {len(files)} files; results: {dict(counts)}")


if __name__ == "__main__":
    main()
