# Start here: data and code map

For a team member who did not write the code. Facts checked on 2026-10-22. How to run things
is in [CLAUDE.md](CLAUDE.md); current status in [ONGOING.md](ONGOING.md); durable gotchas in
[KNOWLEDGE.md](KNOWLEDGE.md).

## Where things live

| Place | Holds | Size |
|---|---|---|
| `~/HTA11/` (git) | code (`scripts/`), notes (`record/`, `report/`), figures, slides, console | ~0.5 MB notes + figures |
| `/nfs-stor/yuqi.lei/HTA11/data/` | downloaded inputs, never edited | 3.7 GB total with `derived/` |
| `/nfs-stor/yuqi.lei/HTA11/derived/` | everything our scripts compute | ~120 MB |
| `/nfs-stor/yuqi.lei/HTA11/logs/` | Slurm stdout/stderr, `<name>_<jobid>.out/.err` | small |
| `/nfs-stor/yuqi.lei/venvs/hta11` | Python env (scanpy, PyDESeq2, gseapy) | — |

Large data never goes in `$HOME`. Anything heavier than a quick look runs through Slurm
(`sbatch scripts/<name>.sh`).

## Input data we hold

| File (under `data/`) | What it is | Shape and units |
|---|---|---|
| `vanderbilt_cellxgene/vanderbilt_dis_epithelial.h5ad` (1.5 GB) | single-cell RNA, epithelial cells, discovery cohort (DIS) | 65,088 cells × 33,703 genes |
| `vanderbilt_cellxgene/vanderbilt_val_epithelial.h5ad` (1.1 GB) | same, validation cohort (VAL), different people | 57,723 cells × 30,104 genes |
| `vanderbilt_cellxgene/vanderbilt_dis_val_non_epithelial.h5ad` (0.14 GB) | immune and stromal cells, both cohorts | 10,696 cells × 28,998 genes |
| `osf_hftq2/ST_master/*_master.h5ad` (7 files, ~0.1 GB each) | Visium spatial, one polyp section each (3 conventional, 4 serrated) | 229–2,047 spots × 19,207 genes |
| `osf_hftq2/WES/master_depth15_maftools.maf` (42 MB) | somatic mutations from bulk exome, authors' calls | 62,361 variants, 97 samples |
| `osf_hftq2/scRNA/VUMC_NMF/` | the atlas's 30 published gene programs (gene weights) | 1 table |
| `osf_hftq2/scRNA/abnormal_epithelium.h5ad` | malignant epithelium with MSS/MSI labels; `X` not raw counts | not used |
| `osf_mxif/*.csv` | MxIF cell tables from OSF — **all 16 are 0 bytes** | unusable |
| `htan_portal/processed_syn_data.json` | HTAN release manifest used for the access audit | metadata |

### How the single-cell files are stored

- Assay: **TruDrop** (an inDrop-style droplet method), 3'-end counting. Median ~2,000–2,400
  genes detected per cell. The authors already removed low-quality cells (dropkick).
- `raw/X`: **raw integer UMI counts**, sparse. This is what every script reads.
- `X`: a **dense normalised float** copy, ~9 GB in memory. Never load it; never call
  `sc.read_h5ad` on the whole file on the login node. Scripts read `raw/X` and `obs` with h5py.
- `obs` (one row per cell): `donor_id`, `HTAN Specimen ID`, `Sample_Classification`
  (NL normal / AD conventional / SER serrated / UNC cancer), `Polyp_Type` (TA, TVA or TV, SSL,
  HP), `Cell_Type` (nine epithelial types incl. ASC and SSC), `tissue` (colon site), `sex`.
- `obsm/X_umap`: the authors' embedding. Our own label-free one is in `derived/label_free/`.

Cell-type codes: STM stem, TAC transit-amplifying (dividing), ABS mature absorbing, GOB goblet,
EE enteroendocrine, TUF tuft, CT crypt-top, **ASC adenoma-specific**, **SSC serrated-specific**.

### How the spatial files are stored

- Chemistry **`Spatial 3' v1`** (10x Visium, **fresh frozen**, poly-A 3' capture; not FFPE).
  Spots are 55 µm wide, 100 µm apart, ~1–10 cells each. Median ~1,300 UMIs and ~640 genes per spot.
- `X`: raw integer counts (dense, small). `obsm/spatial`: pixel coordinates; `uns/spatial`:
  the H&E image and scale factors.
- `obs` per spot: `pathology_annotation` (adenoma, adenoma_border, normal_mucosa, smooth_muscle,
  lymphoid_follicle), `CNV clone` and `cnv_score` (authors' copy-number inference), the published
  program scores (`*_VUMCrefNMF30`), `MILWRM Domain`, and section-level clinical fields.
- Only 4 sections have normal-mucosa spots. Only donor HTA11_10711 is also in our single-cell data.

### What we do not have

- **No sequencing reads** (FASTQ/BAM) for any assay: they are HTAN Level 1/2, behind dbGaP.
  So we cannot call mutations (SNVs) in cells or spots ourselves.
- The three Synapse-only single-cell objects (blocked by a governance issue), so our paired cohort
  is 19 conventional + 15 serrated people, not 28 + 21.
- MxIF only as raw images (needs a free CRDC account plus our own cell segmentation). No ATAC in
  HTA11; the only chromatin data in reach is the Stanford GSE201348 cohort (different people).

## Derived outputs and the script that makes each

| `derived/` folder | Made by | Holds |
|---|---|---|
| `pseudobulk/` | `build_pseudobulk.sh` | per-cell QC table, per-sample and per-sample × cell-type summed counts, cell-type counts |
| `paired/` | `paired_analysis.sh` | polyp vs own normal DESeq2 per route, shared vs route-specific genes, DIS→VAL replication, GSEA |
| `visium/` | `visium_scoring.sh`, `visium_marker_calls.sh` | spot scores, lesion vs normal AUCs, marker-gene spot calls |
| `hypothesis/` | `hypothesis_checks.sh`, `pairing_benefit.sh`, `marker_check.py` | checks X1–X6, label marker check |
| `cell_matching/` | `cell_matching.sh` | same-person optimal-transport matching (step 4) |
| `label_free/` | `label_free_view.sh`, `crypt_axis_scores.sh` | our own UMAP/PCA, look-alike shares, stem/mature scores |

Order: `build_pseudobulk` first (everything else reads its `*_cells.tsv.gz`), then the rest in any
order. Figures: `make_figures.py`, `make_story_figures.py`, `make_he_panels.py` (login node, seconds).
Each analysis is described, with its numbers, in the weekly `report/MM_DD_report.md`.
