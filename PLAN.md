# Project plan

## Completed foundation

- First paper record, public-supplement retrieval, and metadata-audit scripts.
  Evidence and decisions are in `report/09_18_report.md` and `report/09_18_record.md`.
- Git initialization and GitHub remote setup for `CyclopsRay/WhatsTheCancerType`.

## Next phase — select a reproducible research question

1. Resolve specimen/library/participant mappings and the published cohort-count
   differences using source metadata before pooling assays.
2. Inventory public versus controlled-access human data and mouse GEO files.
3. Select the scientific analysis and required inputs; only then configure its
   environment and Slurm resources. Substantive processing runs through Slurm.

## Pending decisions

- Target biological question and whether to prioritize mouse or human data.
- Sequencing data access and persistent storage location outside the home directory.
- Compute environment and Slurm resource profile for the selected analysis.
