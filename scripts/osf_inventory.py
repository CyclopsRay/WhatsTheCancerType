"""Walk the anonymous OSF deposit hftq2 and print one TSV row per entry.

Columns: path, kind, size_bytes, md5, download_url. An md5 of
d41d8cd98f00b204e9800998ecf8427e marks a zero-byte (empty) file.
Usage: python3 scripts/osf_inventory.py > inventory.tsv
"""
import json
import urllib.request

ROOT = "https://api.osf.io/v2/nodes/hftq2/files/osfstorage/"


def entries(url):
    while url:
        page = json.load(urllib.request.urlopen(url, timeout=60))
        for x in page["data"]:
            a = x["attributes"]
            sub = x["relationships"]["files"]["links"]["related"]["href"] if a["kind"] == "folder" else None
            md5 = a["extra"]["hashes"]["md5"] if a["kind"] == "file" else ""
            yield a["materialized_path"], a["kind"], a["size"], md5, x["links"].get("download", ""), sub
        url = page["links"].get("next")


def walk(url):
    for path, kind, size, md5, dl, sub in entries(url):
        print(path, kind, size if size is not None else "", md5, dl, sep="\t", flush=True)
        if sub:
            walk(sub)


if __name__ == "__main__":
    print("path\tkind\tsize_bytes\tmd5\tdownload_url")
    walk(ROOT)
