# HTA11 — Weekly Report, week ending Friday 2026-09-18

Reporting interval: [2026-09-11T18:00:00+04:00, 2026-09-18T18:00:00+04:00) — Asia/Dubai.

Measured results only, with provenance; include positive and negative findings.

## 2026-09-17 — initialization result

- The project contains a documented scaffold (`CLAUDE.md`, `ONGOING.md`,
  `KNOWLEDGE.md`, and `PLAN.md`) and current-week report pair. Provenance:
  filesystem inspection of `/home/yuqi.lei/HTA11` before initialization.

## 2026-09-17 — Supplementary Table 4 metadata audit

Source: [Islam et al., Supplementary Table 4](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-024-07954-4/MediaObjects/41586_2024_7954_MOESM6_ESM.xlsx).
Output: [`table4_audit.json`](../record/001_temporal_recording/table4_audit.json).
Reproduce with `python3 scripts/audit_table4.py`; this recounts supplied metadata,
not raw sequencing reads or independently inferred clonality.

| Measurement | Observed value | Worksheet / field |
|---|---:|---|
| Profiled polyp cohort | 116 rows | HTAN_Vanderbilt |
| Adenoma / serrated / unstated | 70 / 42 / 4 | HTAN_Vanderbilt / Sample_type |
| Distinct participant IDs in cohort sheet | 95 | HTAN_Vanderbilt / HTAN_ID |
| Human WES specimens | 96 (63 AD, 33 SER) | WES_human_polyps |
| Human WES with at least 3 APC mutations | 14/96 (14.58%) | WES_human_polyps / APC_mut_count |
| TCPS with at least 3 APC mutations | 57/300 (19.00%) | TCPS_Human_APC_count / #APC_mut |
| Mouse WES with at least 3 Apc mutations | 5/13 (38.46%) | Mouse_tumor_analysis / first table |
| scRNA analysis rows / distinct specimen IDs | 121 / 114 | scRNAseq_human_polyps / HTAN_SPECID |
| scRNA rows with numeric median VAF | 86 | scRNAseq_human_polyps / Median_VAF |

The source article reports 418 polyps overall and 96 patients in the profiled
cohorts; these totals are not fully reconciled by this workbook audit. See the
[weekly record](09_18_record.md) for follow-up decisions. The source workbook
SHA-256 and audit timestamp are stored with the output above.

## 2026-09-17 — candidate dataset endpoint checks

Source/provenance: [`access_checks.tsv`](../record/002_dataset_choice/access_checks.tsv).
Checks used `curl -fILsS --max-time 30` against public NCBI supplementary endpoints.

| Resource | HTTP status | Interpretation |
|---|---:|---|
| GSE201348 processed matrix archive | 200 | Endpoint reachable; not downloaded or parsed |
| GSE132465 UMI matrix | 200 | Endpoint reachable; not downloaded or parsed |
| GSE132465 cell annotation | 200 | Endpoint reachable; not downloaded or parsed |

These checks establish endpoint availability only. They do not establish matrix
integrity, cohort suitability, or HTA11 RNA access. User-reported HTA11 DNA access
restriction and planning decisions are in the [weekly record](09_18_record.md).

## 2026-09-17 — verified public Vanderbilt scRNA downloads

Source: CELLxGENE public collection for Chen et al. 2021; metadata API queried
at collection ID `a48f5033-3438-4550-8574-cdff3263fdfd`. Direct H5AD URLs were
tested with HTTP HEAD only—no large matrices were downloaded.

| Object | Cells | Download size | HTTP result |
|---|---:|---:|---:|
| Discovery epithelial | 65,088 | 1,524,773,102 bytes | 200 |
| Validation epithelial | 57,723 | 1,145,423,183 bytes | 200 |
| Discovery + validation non-epithelial | 10,696 | 144,074,797 bytes | 200 |

The direct no-login links, donor counts and disease/tissue coverage are recorded
in the [weekly record](09_18_record.md). Endpoint reachability does not substitute
for a Slurm-side H5AD load and metadata audit.

## 2026-09-17 — direct Vanderbilt H5AD download complete

Source: public CELLxGENE assets; download job `256252`. Destination:
`/l/users/yuqi.lei/HTA11/data/vanderbilt_cellxgene/`.

| File | Expected / observed bytes | SHA-256 |
|---|---:|---|
| `vanderbilt_dis_epithelial.h5ad` | 1,524,773,102 / 1,524,773,102 | `2e2b5aa4909fd314ea0c6dba17f6ced16de95c1bb3317e69a3edfe2caff17440` |
| `vanderbilt_val_epithelial.h5ad` | 1,145,423,183 / 1,145,423,183 | `f51bf02885d637073743093844c1db00a173196f0e1184b37f39a5118468668d` |
| `vanderbilt_dis_val_non_epithelial.h5ad` | 144,074,797 / 144,074,797 | `509083fa75d8e22690a444e22c132c2fe7914ed0a9bca55cb0c176c9c07ac39d` |

The byte-size checks and checksums establish a complete transfer only; H5AD
content has not yet been opened or audited.

## 2026-09-17 — exhaustive Stanford GEO/ENA access checks

Scope: Becker 2022 / GSE201349, not the complete HTAN Stanford atlas.
Evidence: [final summary](../record/003_stanford_access/summary.json),
[methods and per-file evidence](../record/003_stanford_access/README.md).
Final summary generated at 19:11 UTC / 23:11 Dubai. Anonymous two-byte GETs;
no complete sequencing datasets downloaded and no checksum integrity claim.

| Resource | Libraries | Files passing transport and content-metadata checks |
|---|---:|---:|
| Processed RNA | 72 | 216/216 |
| Processed ATAC | 89 | 178/178 |
| Exported RNA FASTQ | 72 | 72/72 |
| Exported ATAC FASTQ | 89 | 175/178 |

All 644 listed URLs were checked. Initial 12 timeouts and 11 HTTP 403s cleared
on retry. Three raw ATAC files nevertheless failed content validation on repeat:
SRR18899349_2.fastq.gz reported only 4,096 bytes rather than 9,775,143,964;
SRR18899351_2.fastq.gz and SRR18899357_2.fastq.gz redirected to 802-byte HTML
resources. Provenance: `retry_content_mismatch.jsonl` in the audit directory.
The remaining 247 FASTQ sizes matched the ENA manifest. Processed RNA totals
1,307,185,264 bytes and processed ATAC 124,942,366,931 bytes from Content-Range.
These size observations are not evidence of full-file integrity.

All supplementary-table GEO titles reconcile with the deposited library
inventory: 64 HTAN + 8 HuBMAP RNA, and 80 HTAN + 9 HuBMAP ATAC. These are library
counts, not independent donors or post-QC samples. Complete original 10x barcode
reads and bulk WGS/WES access remain unverified.

## 2026-09-17 — CELLxGENE metadata recheck for roadmap feasibility

Source: [public collection API](https://api.cellxgene.cziscience.com/curation/v1/collections/a48f5033-3438-4550-8574-cdff3263fdfd).
Preserved response: [cellxgene_collection.json](../record/004_roadmap_scope/cellxgene_collection.json).
This check reads collection metadata only; no H5AD observations were loaded.

| API observation | Result |
|---|---|
| Current exposed dataset assets | 3: DIS epithelial, VAL epithelial, combined non-epithelial |
| Separately titled Abnormal asset | 0, although the collection description mentions one containing CRC cells |
| DIS epithelial disease vocabulary | Normal, TA, TVA, SSL, HP, broad colorectal neoplasm |
| VAL epithelial disease vocabulary | Normal, TA, TVA, SSL, HP, colorectal cancer |
| Exact CRC pathology, MSI status and donor replication within H5ADs | Not established by this metadata check |

These observations establish the current API inventory, not the presence or
absence of a usable CRC analysis group. Follow-up decisions and primary-paper
spatial evidence are in [record 004](../record/004_roadmap_scope/README.md).
