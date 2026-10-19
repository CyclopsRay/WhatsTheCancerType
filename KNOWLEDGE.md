# Project knowledge

## Durable facts

- **2026-10-19: OSF `MxIF/quantification/` is empty.** All 16 `*_threshold_quantification.csv`
  files are 0 bytes (md5 `d41d8cd98f00b204e9800998ecf8427e`). The "pre-segmented MxIF
  shortcut" noted below does not exist; MxIF would need segmentation from Level-2
  images. Spatial uses the OSF `ST_master` Visium H5ADs instead: raw int counts,
  `pathology_annotation` per spot (adenoma / adenoma_border / normal_mucosa /
  smooth_muscle / lymphoid_follicle), CNV clone, and the published NMF scores. Only
  4 polyp captures have normal-mucosa spots (8270_1, 8270_2 TA; 8270_3, 8270_5 SSL/HP),
  and only HTA11_10711 overlaps our scRNA donors.
  [Inventory](record/006_feasibility/osf_hftq2_inventory.tsv).
- **The CELLxGENE epithelial H5ADs carry raw integer counts in `raw/X`**; `X` is a
  dense, gzip-chunked normalized float matrix (~9 GB in memory) — read `raw/X` with
  h5py, never `sc.read_h5ad` the whole object on the login node. `Cell_Type` has nine
  states incl. lesion states ASC (adenoma-specific) and SSC (serrated-specific).
- **Per-object paired donors:** DIS conventional 11, serrated 9; VAL 8 and 6. The
  19 / 15 held-data figures are these summed. Any per-cohort fit runs on 6–11 donors;
  with 6 donors the minimum two-sided signed-rank p is 0.031.
- **HP polyps carry SSC like SSL** (median 17–22 % vs 16–23 % of epithelium), so
  pooling HP with SSL as "serrated" is compositionally supported.
- No R on this host. DESeq2 runs through PyDESeq2 0.5.2 in
  `/l/users/yuqi.lei/venvs/hta11` (venv over the promotervi env, adds pydeseq2, gseapy).
  No node.js either. Hallmark GMT cached at `/l/users/yuqi.lei/HTA11/data/genesets/`.
- OSF `scRNA/abnormal_epithelium.h5ad` (42 MB) has MSS/MSI labels on malignant
  epithelium (`Tumor_Type` MSS 2,434 / MSI 272 cells) but `X` is not raw counts.

- **Corrected 2026-09-18.** The earlier claim that Vanderbilt provides no usable
  DNA-sequencing result files including Level 3 is wrong. The HTAN release
  manifest lists 253 open Bulk DNA **Level 3 VCFs** on Synapse over 153
  participants, 85 of them shared with the scRNA Level-4 participants, plus
  maftools-ready somatic calls on OSF. Whether those calls are usable somatic
  calls is a separate, open question — the filenames are GATK germline-style.
  Treat DNA as *available but unvalidated*, and as an optional axis, never a
  dependency. [Access audit](record/005_open_access_audit/README.md). The Stanford
  part of the original claim is untouched. Portal counts are files, not specimen
  or donor counts. Three public Vanderbilt CELLxGENE RNA objects have been
  downloaded; the exact analysis cohort is still an unresolved check.
- The normal-to-polyp-to-cancer project remains feasible as a cross-sectional,
  stage-associated cell-state and spatial-architecture study using RNA, MxIF and
  10x Visium where their pathology metadata and access support the contrasts. It
  cannot claim somatic mutations, founder clonality, phylogeny, or observed
  longitudinal progression without DNA/lineage data.
- **Superseded 2026-09-18** by a machine audit of the HTAN release manifest; the
  manually browsed counts of 2026-09-17 (scRNA L3 224, Visium L3 160, MxIF 126,
  H&E 18) were from an older release. Current open-access HTA11 inventory, in
  files / biospecimens / participants: scRNA L3 364/245/130, scRNA L4 6/210/106,
  Visium L3 170/32/31, Visium L4 43/32/31, Visium auxiliary TIF 47, MxIF L2
  240/46/45, H&E L2 50/50/50, CODEX L2 20/20/20, GeoMx DSP L2 20/20/20, Bulk DNA
  L3 VCF 253/174/153. The portal header now reports 192 cases and 429
  biospecimens. Only Level 1/2 raw sequencing sits behind dbGaP.
  [Audit and derived tables](record/005_open_access_audit/README.md).
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
  alone do not verify the CRC/MSS analytical cohort.
- **Measured 2026-09-18.** DIS and VAL share exactly **one** donor and zero
  specimens (DIS 62 specimens / 30 donors, VAL 59 / 26). They are effectively
  donor-disjoint and usable as discovery and validation. The earlier note that
  "DIS/VAL donor lists overlap" was wrong.
- **HTA11 pathology lives on the biospecimen record, not the diagnosis record.**
  HTA11 diagnosis entries are almost entirely "Not Reported". Use
  `TumorTissueType` plus the ICD-O-3 `HistologicMorphologyCode`: M82110 tubular
  adenoma, M82630 tubulovillous adenoma, M82130 serrated adenoma/SSL. 161 HTA11
  biospecimens are "Not Otherwise Specified" — unresolved, not normal.
- **The decisive design fact.** In the open scRNA Level-4 release: normal 90
  specimens / 59 donors, TA 59/49, TVA 7/7, SSL 23/21, HP-atypia 17/17, CRC
  primary 7/7. Within-donor pairs: normal+conventional **28 donors**,
  normal+serrated **21 donors**, normal+CRC only **3**. Normal-to-polyp is a
  paired donor-replicated design; polyp-to-carcinoma is not. Do not plan a
  three-stage main contrast on this release.
- Spatial: Visium Level 4 has 43 captures over 31 participants but only **7 polyp
  captures** and 10 participants shared with scRNA. MxIF Level 2 has 46
  biospecimens / 45 participants including 28 polyps, and **32** participants
  shared with scRNA. For a polyp question MxIF is the better-matched assay
  despite being released as images.
- `https://osf.io/hftq2/` is fully anonymous and carries the authors' processed
  derivatives: per-capture Visium H5ADs (`ST/`, `ST_master/`), the published k=30
  NMF gene spectra (`scRNA/VUMC_NMF/`), and — critically —
  `MxIF/quantification/`, 16 per-specimen segmented threshold cell tables. That
  removes whole-slide segmentation from any MxIF arm's critical path. **Wrong — the files are empty; see 2026-10-19 entry above.**
- Three Level-4 scRNA H5ADs exist on Synapse but not in the CELLxGENE collection:
  `VUMC_ABNORMALS_EPI_V2.h5ad` (syn27056096), `VUMC_HTAN_NEWCo_EPI_V2.h5ad`
  (syn51069188), `VUMC_HTAN_All_NonEPI_V2.h5ad` (syn51069186). This resolves the
  missing-"Abnormal"-object question. Each also mirrors to ISB-CGC BigQuery.
- Access tiers for HTA11: anonymous (OSF, CELLxGENE, MxIF Minerva viewers);
  free account with no review (Synapse Level 3/4, CRDC-GC/SB-CGC open-access
  imaging); dbGaP Data Access Request (every Level 1/2 raw sequencing file).
  Nothing the project needs is in the third tier.
- HTA11 has four linked publications: Chen 2021 Cell, Heiser 2023 Cell, Islam
  2024 Nature, and Cottam 2025 Nature Communications.

- **What we actually hold versus the full release.** The three downloaded
  CELLxGENE objects are 121 specimens / 55 donors (DIS+VAL epithelial), not the
  210 / 106 of the full six-object Level-4 release. Paired within-donor counts in
  the held data: **normal+conventional 19 donors, normal+serrated 15 donors**,
  normal+CRC 5, both routes 1. The 28 / 21 figures quoted in earlier planning are
  full-release numbers and require the three Synapse-only objects. User reports
  2026-09-18 that Synapse access is blocked by a governance issue; unverified
  from this host.
- **H5AD `obs` carries the join and the labels.** `HTAN Specimen ID`, `donor_id`,
  `Sample_Classification` (NL / AD / SER / UNC, and MSS / MSI-H in the
  non-epithelial object), `Polyp_Type` or `Tumor_Type`, `disease`, `tissue`,
  `Cell_Type`, `sex`, `self_reported_ethnicity`. The Week-1 cohort gate is
  passed: the within-donor paired design is constructible.
- **Carcinoma subtype is not annotated in the epithelial objects.** All malignant
  specimens are a single `UNC` bucket: 7 donors, 5,514 cells, `disease` reading
  "colorectal neoplasm" (DIS, 2 specimens) or "colorectal cancer" (VAL, 5). MSS
  and MSI-H appear only in the non-epithelial object, at **5 and 2 donors**.
  Subtyped malignant epithelium is presumably in `VUMC_ABNORMALS_EPI_V2.h5ad`,
  which we do not hold. Any "across cancer types" question is unsupported in the
  scRNA data we can currently obtain.
- The only well-powered MSS/MSI material found is the spatial atlas on OSF:
  `WES/master_depth15_clinicalData.txt` types 97 samples MSS 48 / MSI 37, and the
  `ST_master/` Visium captures are joinable to those barcodes. Different donors
  from the scRNA cohort, and carcinoma-versus-carcinoma, not polyp-to-carcinoma.
- **Anatomical site is confounded with donor.** `tissue` resolves seven colorectal
  sites, but every donor carries exactly one site label, so the matched normal is
  site-matched to its polyp by construction and site can only be tested between
  donors.
- `Polyp_Type` vocabulary differs across objects: DIS writes `TVA`, VAL writes
  `TV`. Harmonize before pooling.

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
