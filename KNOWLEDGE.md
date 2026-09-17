# Project knowledge

## Durable facts

- User reports that HTAN Stanford and Vanderbilt provide no usable DNA-sequencing
  result files, including Level 3, as of 2026-09-17. Treat DNA as unavailable.
  [Snapshot and evidence](record/002_dataset_choice/README.md). Portal counts are
  files, not specimen or donor counts. Three public Vanderbilt CELLxGENE RNA
  objects have been downloaded; atlas-wide RNA access and the exact analysis
  cohort are separate, unresolved checks.
- The normal-to-polyp-to-cancer project remains feasible as a cross-sectional,
  stage-associated cell-state and spatial-architecture study using RNA, MxIF and
  10x Visium where their pathology metadata and access support the contrasts. It
  cannot claim somatic mutations, founder clonality, phylogeny, or observed
  longitudinal progression without DNA/lineage data.
- Vanderbilt public-file inventory supplied by the user lists: scRNA-seq Level 3
  (224 Synapse files) and Level 4 (6); 10x Visium Level 3 (160), Level 4 (40)
  and auxiliary (40); MxIF Level 2 (126 CRDC/GC files); and H&E Level 2 (18
  CRDC/GC files). These are file—not participant or specimen—counts. The public
  portal documentation reports 90 cases and 193 biospecimens for the Vanderbilt
  Colon Atlas, but the three-stage subset must be reconstructed from metadata.
- The public CELLxGENE Vanderbilt collection has three no-login H5AD assets,
  verified HTTP 200 on 2026-09-17: DIS epithelial (65,088 cells, 1.52 GB, 30
  donors), VAL epithelial (57,723 cells, 1.15 GB, 26 donors), and combined
  non-epithelial (10,696 cells, 144 MB). The published collection description
  specifies 128 independent scRNA-seq datasets on 62 tumours and includes two
  MSI-H plus five MSS fresh CRC specimens in the abnormal-cell data.
- Project duration: ten weeks. User's chosen direction: normal-to-adenoma-to-cancer
  cell-state changes. Course roadmap is due the evening of 2026-09-17; two members
  each write their own version manually. AI brainstorming is allowed, but generated
  submission prose is not. Team: Yuqi Lei and Muhammed Bah. Course-required
  modalities remain unspecified; the user's proposed question includes spatial patterns.
- Current primary candidate: Vanderbilt/Chen RNA; Stanford GSE201348 and GSE132465
  remain external-support options. All 216 Stanford processed RNA components
  (72 libraries) and 178 processed ATAC components (89 libraries) passed anonymous
  two-byte GET checks on 2026-09-17. Representative file contents also passed
  format checks. Full matrix integrity and exact analysis cohort remain unaudited.
  See `record/003_stanford_access/`. Bulk WGS access and complete original 10x
  barcode/technical reads remain unverified. Healthy normal and
  unaffected FAP tissue must be distinguished; repeated polyps share donors.
- The exhaustive Stanford GEO/ENA audit checked 644 URLs. All 72 exported RNA
  FASTQs passed access/content-metadata checks; only 175/178 ATAC FASTQs passed:
  SRR18899349_2 had a size mismatch, and SRR18899351_2 / SRR18899357_2 returned HTML.
  These exceptions persisted on recheck, while initial timeouts/403s cleared.
  HTTP 206 alone is insufficient evidence of a valid sequencing download.
  See [final access audit](record/003_stanford_access/README.md); processed files
  remain fully reachable, but neither whole-file integrity nor bulk DNA access
  was established.
- User clarified on 2026-09-17 that “race types” means disease/polyp subtypes.
  Proposed main route: normal/non-neoplastic mucosa, conventional TA/TVA, and
  documented MSS colorectal adenocarcinoma; exact analytical subset remains open.
- Heiser et al. 2023 spatial cohort contains 31 specimens: 12 MSS CRC, 10 MSI-H
  CRC, four TA/TVA, four SSL/HP and one normal. A single normal is a descriptive
  spatial reference, not replicated control evidence. Actual accessible spatial
  files and matching remain unaudited. See [scope evidence](record/004_roadmap_scope/README.md).
- CELLxGENE's collection description mentions a CRC-containing “Abnormal” object,
  but its API currently exposes three other titled assets. Disease vocabularies
  alone do not verify the CRC/MSS analytical cohort. DIS/VAL donor lists overlap;
  independent-donor validation and three-stage coverage need explicit auditing.
- The project directory was empty when initialized on 2026-09-17.
- The source study is Islam et al. (2024), DOI 10.1038/s41586-024-07954-4.
  Its main disease is colorectal precancer; mouse engineered lineage tracing and
  human endogenous-variant inference are distinct assay arms.
- Sample counts have different units and subsets. Do not interpret the headline
  418 polyps as 418 matched single-cell/exome specimens. See the first
  [research record](record/001_temporal_recording/README.md) for the audit and open discrepancies.
- Supplementary Table 4 contains multiple tables in the mouse sheet; counting
  every populated row as a tumour overcounts specimens. Use `scripts/audit_table4.py`.
- `rg` is unavailable on this host; use `find` and `grep` as fallbacks.
- GitHub repository: `CyclopsRay/WhatsTheCancerType`, local default branch `main`.
  Existing host SSH authentication can access it; HTTPS Git access had no usable
  credentials during setup. Use the SSH `origin` for host-side fetch/push.
- The initial read-only `.git` seen inside the sandbox was a placeholder: an
  approved host-side check found no actual directory. Approved `git init` created
  normal metadata without replacing an existing repository.
