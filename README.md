# WhatsTheCancerType

Research notes and reproducible inspection scripts for understanding the cancer
types, experimental systems, and datasets in tumour-atlas studies.

The first review covers **Temporal recording of mammalian development and
precancer**, Islam et al., Nature (2024),
[DOI: 10.1038/s41586-024-07954-4](https://www.nature.com/articles/s41586-024-07954-4).
It distinguishes mouse lineage-tracing experiments from human colorectal
precancer profiling and audits the published supplementary sample counts.

## Start here

- [First paper review](record/001_temporal_recording/README.md)
- [Research record index](record/README.md)
- [Weekly results](report/09_18_report.md) and [discussion](report/09_18_record.md)
- [Project operating guide](CLAUDE.md) and [forward plan](PLAN.md)

## Reproduce the supplementary-table audit

Requirements: Python 3 and curl. No third-party Python packages are required.

```bash
git clone https://github.com/CyclopsRay/WhatsTheCancerType.git
cd WhatsTheCancerType
python3 scripts/fetch_paper_sources.py --download
python3 scripts/audit_table4.py
```

The download script retrieves two small public supplements and prints their
SHA-256 hashes. The audit recounts supplied metadata; it does not reprocess raw
sequencing reads. Downloaded supplements, Python caches, and logs are excluded
from version control. The saved audit includes the original host path for
provenance; scripts locate the project relative to their own files.

Weekly records use the ending Friday and roll over at 18:00 Asia/Dubai.
`scripts/ensure_week.sh` depends on the research-week helper installed on the
author's HPC host; it is not needed to download or audit the supplements.

This repository contains research documentation and inspection utilities, not
a trained cancer-classification model. See the paper review for source links
and unresolved specimen-count differences.
