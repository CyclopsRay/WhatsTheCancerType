#!/usr/bin/env python3
"""Read supplementary DOCX text or audit XLSX rows using only the Python standard library."""

import argparse
from collections import Counter
import json
from pathlib import Path
import posixpath
import xml.etree.ElementTree as ET
import zipfile

NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def xlsx_sheets(path):
    with zipfile.ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(t.text or "" for t in si.findall(".//s:t", NS))
                       for si in root.findall("s:si", NS)]
        links = {r.attrib["Id"]: r.attrib["Target"] for r in
                 ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))}
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        for sheet in book.findall("s:sheets/s:sheet", NS):
            target = links[sheet.attrib[f"{{{REL}}}id"]]
            target = target.lstrip("/") if target.startswith("/") else posixpath.normpath("xl/" + target)
            root = ET.fromstring(archive.read(target))
            rows = []
            for row in root.findall("s:sheetData/s:row", NS):
                values = {}
                for cell in row.findall("s:c", NS):
                    column = "".join(c for c in cell.attrib["r"] if c.isalpha())
                    kind = cell.get("t")
                    value = cell.findtext("s:v", default="", namespaces=NS)
                    if kind == "s" and value:
                        value = strings[int(value)]
                    elif kind == "inlineStr":
                        value = "".join(t.text or "" for t in cell.findall(".//s:t", NS))
                    if value.strip():
                        values[column] = value
                if values:
                    rows.append({"excel_row": int(row.attrib["r"]), "values": values})
            yield sheet.attrib["name"], rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--sheet", help="Only inspect the named XLSX sheet")
    parser.add_argument("--rows", type=int, default=3, help="Preview data rows per sheet")
    parser.add_argument("--column", help="Count values in an Excel column, e.g. D; excludes first populated row")
    args = parser.parse_args()
    if args.path.suffix.lower() == ".docx":
        with zipfile.ZipFile(args.path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        for paragraph in root.findall(".//w:p", ns):
            text = "".join(t.text or "" for t in paragraph.findall(".//w:t", ns))
            if text.strip():
                print(text)
        return
    if args.path.suffix.lower() != ".xlsx":
        parser.error("Expected a .docx or .xlsx file")
    matched = False
    for name, rows in xlsx_sheets(args.path):
        if args.sheet and args.sheet != name:
            continue
        matched = True
        result = {"sheet": name, "populated_rows": len(rows),
                  "header": rows[0] if rows else None,
                  "data_rows_after_header": max(0, len(rows) - 1),
                  "preview": rows[1:1 + max(0, args.rows)]}
        if args.column:
            result["column_counts"] = dict(Counter(
                row["values"].get(args.column.upper(), "<empty>") for row in rows[1:]))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    if not matched:
        parser.error("No matching worksheet")


if __name__ == "__main__":
    main()
