# HTA11 operating guide

## Project setup

Initial work reviews the HTAN Vanderbilt colorectal precancer study by Islam
et al. (2024). Start at `record/001_temporal_recording/README.md` for the paper,
assays, source links, and reproducible inspection commands.
Current planning also considers Stanford's RNA cohort for a ten-week study of
normal/adenoma/CRC states; see `record/002_dataset_choice/README.md` and `PLAN.md`.
Vanderbilt RNA is the current primary candidate. Latest subtype and spatial
feasibility evidence is in `record/004_roadmap_scope/README.md`; earlier Stanford
primary recommendations are historical. Internal planning files are AI-assisted
notes, not prose for either student's manually written submission.
HTA11 DNA Level 3 is unavailable to the user. Assignment writing constraints are
recorded in `KNOWLEDGE.md`; `ROADMAP_WORKSHEET.md` is a planning aid, not a submission.

## Layout and commands

- `record/`: numbered research topics and small provenance outputs.
- `scripts/`: lightweight source retrieval and metadata inspection utilities.
- `report/`: weekly decisions and measured results, eligible for git tracking.
- `python3 scripts/fetch_paper_sources.py --download`: retrieve public supplements.
- `python3 scripts/audit_table4.py`: recount downloaded Supplementary Table 4.
- `python3 scripts/audit_stanford_access.py --help`: inventory and bounded
  per-file access checks; see `record/003_stanford_access/README.md` for inputs.
- `bash scripts/ensure_week.sh`: select/create this week's report pair before writing.

Utilities use Python 3 standard library and curl; the reporting wrapper calls
`/home/yuqi.lei/.local/bin/research-week`. Download caches under `record/*/sources/`
are excluded from git. Keep large sequencing data outside the home directory.
Git is initialized on branch `main`. The GitHub repository is
`https://github.com/CyclopsRay/WhatsTheCancerType`; `origin` uses
`git@github.com:CyclopsRay/WhatsTheCancerType.git` with the host's existing SSH
authentication. Git metadata writes and network operations may require sandbox
approval. Keep `report/`, research notes, scripts, and small audit outputs tracked.

## Working conventions

- Read `ONGOING.md`, `KNOWLEDGE.md`, and `PLAN.md` before making project changes.
- Keep `ONGOING.md` limited to active or newly finished work that remains under
  analysis.
- Record durable findings in `KNOWLEDGE.md`, forward work in `PLAN.md`, and dated
  decisions with their reasoning in the current weekly record.
- Record experiments and results in the current weekly files under `report/`.

## Compute and storage

This is an HPC login node. Keep local checks small; submit substantive compute
through Slurm. Keep source and configuration in the project directory and place
large datasets, checkpoints, and caches under `/l/users/$USER`.
