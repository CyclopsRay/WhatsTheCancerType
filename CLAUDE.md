# HTA11 operating guide

## Project setup

Initial work reviews the HTAN Vanderbilt colorectal precancer study by Islam
et al. (2024). Start at `record/001_temporal_recording/README.md` for the paper,
assays, source links, and reproducible inspection commands.
Scope was fixed on 2026-09-18: HTA11 only, within-donor polyp versus matched
normal mucosa, conditioned on conventional/serrated route, with driver genotype
as a droppable extension. See [ROADMAP.md](ROADMAP.md) and `PLAN.md`. Access and
cohort evidence is in `record/005_open_access_audit/README.md`; earlier Stanford
primary recommendations and the three-stage normal/adenoma/CRC framing in
`record/002_dataset_choice/` and `record/004_roadmap_scope/` are historical.
**HTA11 Bulk DNA Level 3 (253 exome VCFs) is open on Synapse** — the earlier
"DNA unavailable" note was wrong and is corrected in `KNOWLEDGE.md`. Only Level
1/2 raw sequencing needs a dbGaP request, and the project does not use it.
Internal planning files are AI-assisted notes, not prose for either student's
manually written submission. Assignment writing constraints are recorded in
`KNOWLEDGE.md`; `ROADMAP_WORKSHEET.md` is a planning aid, not a submission.

## Layout and commands

- `record/`: numbered research topics and small provenance outputs.
- `scripts/`: lightweight source retrieval and metadata inspection utilities.
- `report/`: weekly decisions and measured results, eligible for git tracking.
- `python3 scripts/fetch_paper_sources.py --download`: retrieve public supplements.
- `python3 scripts/audit_table4.py`: recount downloaded Supplementary Table 4.
- `python3 scripts/audit_stanford_access.py --help`: inventory and bounded
  per-file access checks; see `record/003_stanford_access/README.md` for inputs.
- `bash scripts/ensure_week.sh`: select/create this week's report pair before writing.
- Analysis pipeline (Slurm, `cscc-cpu-p` / `cscc-cpu-qos`): `sbatch scripts/build_pseudobulk.sh`,
  `sbatch scripts/paired_analysis.sh`, `sbatch scripts/visium_scoring.sh`; marker-gene spot calls `sbatch scripts/visium_marker_calls.sh`; figures with
  `/nfs-stor/$USER/venvs/hta11/bin/python scripts/make_figures.py /nfs-stor/$USER/HTA11/derived figures`.
  Order and outputs: [record 006](record/006_feasibility/README.md).
  Hypothesis checks: `sbatch scripts/hypothesis_checks.sh` (X1–X5), `sbatch scripts/pairing_benefit.sh`
  (X6) → `derived/hypothesis/`; step-4 matching `sbatch scripts/cell_matching.sh [--test]` →
  `derived/cell_matching/`; label-free UMAP/PCA `sbatch scripts/label_free_view.sh` → `derived/label_free/`, `figures/fig10_*`; stem/mature scores `sbatch scripts/crypt_axis_scores.sh` (same dir); label check `scripts/marker_check.py PB_DIR OUT_DIR` (seconds); talk figures (fig8, fig11–14, fig17): `scripts/make_story_figures.py DERIVED figures`; progress-report figures (report_fig1–5): `scripts/make_report_figures.py DERIVED figures` (seconds); report PDF with figures: `/nfs-stor/$USER/venvs/hta11-doc/bin/python scripts/report_to_pdf.py presentation/progress_report/draft_v1.md presentation/progress_report/progress_report.pdf` (prints page count); person explorer page: `scripts/make_person_explorer.py DERIVED presentation/person_explorer/template.html OUT.html` → https://claude.ai/artifact/Xi6uWPxrpUKZcgz9LL3YDH;
  four next-step models (GPU, each takes `--test`): `sbatch scripts/person_free.sh` (fig18), `scripts/polyp_anomaly.sh` (fig19),
  `scripts/polyp_flow.sh` (fig20), `scripts/visium_mapping.sh` (fig21) → `derived/{person_free,anomaly,flow,visium_mapping}/`;
  H&E polyp panels (slide 2): `scripts/make_he_panels.py /nfs-stor/$USER/HTA11/data/osf_hftq2/ST_master figures` (seconds); add `/nfs-stor/$USER/HTA11/derived/visium/marker_calls_spots.tsv.gz` as a third argument for fig16 (route genes on the same slices).
- Slides follow the global `slide-storytelling` skill (story order, plain words, gray term lines).
- Project analysis env: `/nfs-stor/$USER/venvs/hta11` (scanpy + PyDESeq2 + gseapy). No R, no node.
  Exported specs and rebuild steps: [env/README.md](env/README.md); re-export after installing anything.
- Arms console artifact: `console/index.html` → https://claude.ai/artifact/EAd4sS1nSVmPepYoRBhZpF.
  Update the data arrays at the top and republish after every project change.
  Midterm deck: https://claude.ai/artifact/VVPjMSC6a5dnFAbnEYHG7G (sources in `presentation/`).
- `/nfs-stor/$USER/venvs/hta11-doc/bin/python scripts/md_to_pdf.py FILE.md`: render a
  planning document to PDF. Handles headings, paragraphs and lists only, not
  tables. The venv holds `fpdf2` and `pypdf`; the analysis env is `/nfs-stor/$USER/venvs/hta11`.

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
large datasets, checkpoints, and caches under `/nfs-stor/$USER`.
