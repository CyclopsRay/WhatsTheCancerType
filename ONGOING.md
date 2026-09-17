# Current status

## Active work

- Slurm job `256252` completed the direct download of all three public
  Vanderbilt/CELLxGENE H5AD objects to
  `/l/users/yuqi.lei/HTA11/data/vanderbilt_cellxgene/`. Exact expected byte
  sizes and SHA-256 checksums were verified. Next: a Slurm-side lightweight H5AD
  integrity and metadata load, including exact CRC/MSI coverage and DIS/VAL donor
  overlap; collection metadata alone do not resolve these. No biological analysis
  has begun. Scope evidence is in [record 004](record/004_roadmap_scope/README.md).

## Current reporting interval

Week ending 2026-09-18: [record](report/09_18_record.md),
[results](report/09_18_report.md).
Select again with `bash scripts/ensure_week.sh` before each weekly update.
Forward actions are in [PLAN.md](PLAN.md).
