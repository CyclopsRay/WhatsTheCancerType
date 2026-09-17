# HTA11 — Weekly Record, week ending Friday 2026-09-18

Reporting interval: [2026-09-11T18:00:00+04:00, 2026-09-18T18:00:00+04:00) — Asia/Dubai.

Plans, discussion, decisions, reasoning, and corrections (Chinese or English).

## 2026-09-17 — project baseline

- Initialized the required operating and project-memory documents because the
  directory contained no project files. The project objective and technical stack
  remain unspecified, so no implementation or environment was assumed.

## 2026-09-17 — first paper review and reproducible source inspection

- User requested the first record folder and scripts, beginning with experiments,
  species, and cancer types in Islam et al., DOI 10.1038/s41586-024-07954-4.
- Created `record/001_temporal_recording/` for the topic; retain `report/` for the
  weekly cycle. Read the article, relevant extended-data captions, supplementary
  methods, and Table 4. Retrieved only the two small public supplements.
- Added standard-library scripts for retrieval, DOCX/XLSX inspection, a Table 4
  audit, and a wrapper around the existing week-selection helper. No analysis
  environment or compute allocation is needed for this metadata work.
- Separate engineered mouse barcodes from human natural-mutation inference.
  Do not label human polyp profiling as CRISPR intervention or direct single-cell
  DNA sequencing. Focus is colorectal precancer; external breast tumour data
  validate a method and do not define the clinical cohort.
- Counts need reconciliation before pooling: published headline 418 differs from
  the simple 96 + 300 DNA-cohort sum; cohort metadata have 95 unique HTAN_ID values
  while text reports 96 patients. The scRNA analysis sheet has 121 rows and 114
  distinct specimen IDs; its 86 numeric median-VAF values agree with the stated
  VAF analysis size. No correction to the paper is asserted from this audit alone.
- Next decision: choose the biological analysis after auditing specimen-to-assay
  mappings and data access. Details: `record/001_temporal_recording/README.md`.
- Files remain uncommitted because the protected `.git` scaffold is not a working
  repository; no git metadata was modified.
- Validation: all three Python scripts parse, the Bash wrapper passes `bash -n`,
  DOCX extraction succeeds, repeated retrieval preserves the two source hashes,
  and a fresh audit exactly matches the saved JSON apart from its timestamp.

## 2026-09-17 — GitHub repository setup

- User supplied `https://github.com/CyclopsRay/WhatsTheCancerType.git` and requested
  publishing this project as a GitHub repository. Read-only inspection found the
  remote empty. Existing SSH authentication works; HTTPS lacks credentials, so
  configure `origin` using the equivalent SSH URL.
- Corrected the earlier interpretation of `.git`: the apparent protected
  directory was a sandbox placeholder, absent on the underlying host. Initialized
  Git on `main` through an approved command without replacing existing metadata.
- Added the root README with project scope and reproduction instructions. Include
  operating docs, `report/`, research notes, scripts, and the small audit JSON in
  the initial commit; exclude downloaded source supplements, logs, and caches.
- Publication procedure: commit the reviewed files, push `main` without force,
  and verify the remote branch hash matches local HEAD.
