#!/usr/bin/env python3
"""List or download this record's small public supplements; never overwrite files."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

PROJECT = Path(__file__).resolve().parents[1]
RECORD = PROJECT / "record" / "001_temporal_recording"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Download supplements; default only lists URLs")
    args = parser.parse_args()
    manifest = json.loads((RECORD / "sources.json").read_text())
    for item in manifest["files"]:
        print(f"{item['name']}\t{item['url']}", flush=True)
        if not args.download:
            continue
        folder = RECORD / "sources"
        folder.mkdir(exist_ok=True)
        destination = folder / item["name"]
        if not destination.exists():
            with tempfile.TemporaryDirectory(prefix="fetch-", dir=folder) as scratch:
                temporary = Path(scratch) / item["name"]
                subprocess.run([
                    "curl", "--fail", "--location", "--silent", "--show-error",
                    "--max-time", "45", "--output", str(temporary), item["url"],
                ], check=True)
                validate(temporary)
                # Exclusive creation preserves an existing file even if another fetch races us.
                with destination.open("xb") as output:
                    output.write(temporary.read_bytes())
        validate(destination)
        print(f"sha256={hashlib.sha256(destination.read_bytes()).hexdigest()}  {destination}")


def validate(path):
    expected = "word/document.xml" if path.suffix == ".docx" else "xl/workbook.xml"
    with zipfile.ZipFile(path) as archive:
        if expected not in archive.namelist():
            raise ValueError(f"Not the expected Office document: {path}")
        if archive.testzip() is not None:
            raise ValueError(f"Corrupt Office document: {path}")


if __name__ == "__main__":
    main()
