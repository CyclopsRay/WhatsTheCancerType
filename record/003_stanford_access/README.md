# 003 — Stanford sequencing-access audit

Date: 2026-09-17. Scope: Becker et al., Nature Genetics (2022), DOI
10.1038/s41588-022-01088-x, GEO SuperSeries GSE201349. This is not an audit of
every dataset in the HTAN Stanford atlas.

## Final result — 2026-09-17, 19:11 UTC (23:11 Dubai)

All processed RNA/ATAC components are anonymously accessible. Do **not** claim
that every raw sequencing file or bulk DNA modality is verified.

| Data | Deposited libraries | Files passing access/content-metadata checks |
|---|---:|---:|
| Processed RNA matrices, features, barcodes | 72 | 216/216 |
| Processed ATAC fragments and indexes | 89 | 178/178 |
| Exported RNA FASTQs | 72 | 72/72 |
| Exported ATAC FASTQs | 89 | 175/178 |

Initial checks had 12 timeouts and 11 HTTP 403 responses; all cleared on one
retry at the same public URLs without credentials. Further content-type and
total-size validation found three ATAC exceptions, reproduced on another check:

| ENA file | Expected bytes | Response |
|---|---:|---|
| SRR18899349_2.fastq.gz | 9,775,143,964 | Content-Range total was only 4,096 bytes |
| SRR18899351_2.fastq.gz | 8,459,870,839 | Redirected to an 802-byte HTML resource |
| SRR18899357_2.fastq.gz | 9,023,477,705 | Redirected to an 802-byte HTML resource |

These are unverified FASTQ downloads, not proof that no other public mirror or
SRA archive can supply the reads. All corresponding processed ATAC files passed.
Processed RNA totals 1,307,185,264 compressed bytes; processed ATAC totals
124,942,366,931 bytes. The RNA access result supports the proposed cell-state
analysis, subject to full-file loading, QC and donor/stage metadata checks.

## Evidence and method

- [manifest.json](manifest.json): sample-level GEO links joined to ENA runs by
  experiment accession, enumerating 644 public processed/FASTQ file URLs.
- `checks_*.jsonl`: per-file anonymous HTTP GET requests for bytes 0–1. Each
  transport success requires HTTP 206, curl exit code zero, and exactly two
  transferred bytes. Final file-access validation also requires the expected
  byte range, a non-HTML response and, for FASTQs, total size matching ENA.
  Content-Range records full file size. Transfers use one to three
  connections per batch and are capped; no full sequencing datasets downloaded.
- [sources.json](sources.json): metadata URLs and SHA-256 checksums. The small
  originals are cached under ignored `sources/`.
- [summary.json](summary.json): final exhaustive coverage, content-metadata
  validation and paper-to-GEO title reconciliation. Use `file_access_passed`,
  not merely `range_passed`, for the conclusion.
- `retry_*.jsonl`: later checks, preserving all original attempts.
- `summary_initial.json` and `summary_transport_only.json`: intermediate HTTP-only
  summaries, superseded by the final content-aware summary.

The GEO deposit has 72 RNA libraries (GSE201348) and 89 ATAC libraries
(GSE201336), including replicates. RNA has three processed components per library
(matrix, features, barcodes); ATAC has fragments and indexes. All libraries have
matching ENA run entries. Supplementary Tables S3–S5 supply matching GEO titles:
64 HTAN RNA + 8 HuBMAP RNA, and 80 HTAN ATAC + 9 HuBMAP ATAC.

These are deposited-library counts. The article reports 70 RNA and 80 ATAC
samples after QC, and 81 tissues across the study; these denominators describe
different stages and units. [Primary article](https://www.nature.com/articles/s41588-022-01088-x).

## Boundaries on the conclusion

1. Range requests establish current anonymous access, not checksum integrity of
   every byte, future availability, or biological quality.
2. ENA exposes 72 RNA FASTQs and 178 ATAC FASTQs. The RNA run metadata label all
   libraries PAIRED but list one FASTQ per run and no submitted original-file
   links. Full original 10x technical/barcode read completeness is not verified;
   do not promise a FASTQ-to-Cell-Ranger reproduction from these exports alone.
3. Whole-genome sequencing is reported for eight polyps and one CRC in the
   [supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41588-022-01088-x/MediaObjects/41588_2022_1088_MOESM1_ESM.pdf).
   It is absent from this RNA/ATAC GEO manifest. The public author repository
   contains WGS/WES scripts using local BAM paths, which do not establish public
   data access. WGS/WES access remains unverified; do not promise all DNA data.
4. This audit uses GEO/ENA, not a blanket test of Synapse/HTAN/HuBMAP mirrors.
5. The raw FASTQ manifests total 660,100,599,704 RNA bytes and
   1,421,021,630,413 ATAC bytes (about 2.08 TB combined, decimal). These are listed
   sizes, not data downloaded. Start the project with processed RNA counts.

## Reproduce

Download the five small metadata resources in `sources.json` to `sources/`.
Then, from the project root:

```bash
python3 scripts/audit_stanford_access.py inventory \
  --soft record/003_stanford_access/sources/family.soft.gz \
  --ena record/003_stanford_access/sources/rna_runs.tsv record/003_stanford_access/sources/atac_runs.tsv \
  --output /tmp/stanford_manifest_new.json
python3 scripts/audit_stanford_access.py probe \
  --manifest /tmp/stanford_manifest_new.json --start 0 --limit 100 \
  --output /tmp/stanford_checks_0000_new.jsonl
```

Repeat bounded batches for starts 100, 200, 300, 400, 500 and 600 (last limit 44).
Use fresh output names to preserve original evidence. The `summarize` subcommand
accepts `--manifest`, `--checks` (all seven result files), `--metadata` (the XLSX),
and `--output`. It rejects missing/duplicate file indices or mismatched URLs.
For targeted retries use `probe --indices INDEX ... --timeout 30 --connections 3`.
Supply retry logs to `summarize --rechecks` in chronological attempt order; the
last supplied attempt per file determines the final result. This audit's order
is `retry_timeouts.jsonl`, `retry_remaining.jsonl`, then
`retry_content_mismatch.jsonl`. Five lightweight assertions tested rejection of
HTML, wrong size, wrong byte range, failed transport, and acceptance of a valid
response. Whole-file checksum validation is still pending.

The script uses standard-library Python and curl 8.5.0 on this host. The audit
does not launch analysis jobs, create compute reservations or bypass authentication.
