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

## 2026-09-17 — access restriction and ten-week roadmap brainstorming

- User reports DNA Level 3 inaccessible for governance reasons. Preserve this as
  the operational access constraint even though the supplied screenshot lists
  220 DNA Level 3 files as open on Synapse. Screenshot transcription lives in
  `record/002_dataset_choice/availability_snapshot.tsv`; file counts are not samples.
- User confirmed ten weeks and selected normal-to-adenoma-to-cancer cell-state
  changes as their preferred direction. Team names and course multiomics/ML
  requirements remain unspecified.
- Recommendation changed with that preference: prioritize Stanford/Becker 2022
  GSE201348 RNA for stage coverage, retain HTA11 as reference, use GSE132465 as
  independent CRC endpoint validation. Dataset choice remains a working proposal
  pending full metadata and count-file audit. No expression matrix was downloaded.
- Design concerns: Stanford includes FAP and repeated polyps per donor; healthy
  normal is not equivalent to unaffected FAP. Check estimability before adjusting
  for covariates. Cross-sectional contrasts cannot establish longitudinal
  progression, founder ancestry, or individual polyp progression risk.
- Assignment instructions require each of two students to write their own
  document manually; AI brainstorming is permitted. Created an operational plan,
  evidence notes and a blank writing worksheet, not six completed submission
  answers. No course submission was attempted.
- Keep an RNA-only core with donor-aware expression/composition analysis;
  optional ATAC/trajectory work follows only after core completion or a confirmed
  course requirement. Detailed milestones are in `PLAN.md`.

## 2026-09-17 — exhaustive Stanford deposited-file access audit

- User requested stronger assurance that Stanford sequencing data are accessible.
  Scope is the Becker 2022 paper/GSE201349, not the entire Stanford HTAN atlas.
- Enumerated GEO family metadata and joined ENA experiments: 72 RNA libraries,
  89 ATAC libraries, 394 processed components and 250 exported FASTQs. Library
  titles agree with the paper's supplementary HTAN/HuBMAP mappings.
- Test each file via anonymous two-byte HTTP range GET, recording status, byte
  count and full size from Content-Range. This demonstrates current download
  access without retrieving terabytes or claiming full-file integrity.
- Representative 64-KB prefixes decode as an integer Matrix Market matrix,
  ATAC fragments and FASTQ. All processed components pass access checks.
- ENA labels RNA runs PAIRED but exports one FASTQ per run, with no submitted
  original URLs. Original 10x barcode/technical-read completeness is not established.
- The supplement describes WGS on eight polyps and one CRC, but the cited GEO
  series has RNA and ATAC only. Public WGS/WES scripts refer to local BAM paths;
  that does not establish anonymous DNA access. Keep WGS unverified and outside
  the required project inputs. Detailed evidence: `record/003_stanford_access/`.

## 2026-09-17 — DNA-free multimodal scope clarification

- User clarified that neither HTAN Stanford nor Vanderbilt has usable DNA
  sequencing results, including Level 3. The project therefore must not depend
  on DNA recovery or a DNA-derived fallback.
- The chosen biological goal remains achievable with Vanderbilt RNA for cell-state
  discovery and abundance testing, MxIF for spatially resolved validation of a
  small marker panel, and 10x Visium for tissue-neighborhood and regional
  localization analyses, provided each modality has usable normal, polyp and CRC
  pathology metadata. These modalities answer complementary questions rather
  than replacing one another's measurement resolution.
- Reframe every conclusion as a cross-sectional association with pathology stage:
  do not claim mutations, clonal ancestry, a polyp's future cancer risk, or that
  a particular polyp was directly observed becoming cancer. Do not pool cells or
  spots as biological replicates; donor/specimen remains the inference unit.
- Proposed priority: establish the RNA donor-by-stage inventory and a reproducible
  RNA-only core first; then use Visium and MxIF as targeted spatial corroboration
  after confirming stage coverage, specimen linkage, antibody/panel content and
  sufficient independent donors. Stanford RNA remains a fallback/parallel cohort,
  not a DNA source.

## 2026-09-17 — Vanderbilt public-data inventory and validation design

- Publicly listed Vanderbilt files in the user-supplied portal snapshot: scRNA-seq
  L3 224 and L4 6 (Synapse); Visium L3 160, L4 40 and auxiliary 40 (Synapse);
  MxIF L2 126 and H&E L2 18 (CRDC/GC). Counts are files, not subjects or slides.
  Raw scRNA and Visium L1/L2 are controlled; omit them from the planned workflow.
- HTAN's current portal manual describes the Vanderbilt Colon Atlas as 90 cases
  and 193 biospecimens, but this is atlas-wide, not a guarantee of balanced
  normal/adenoma/CRC coverage within every assay. The public metadata download
  is required before reporting final stage-specific participant counts.
- Separate two Vanderbilt publications/cohorts: Chen et al. 2021 is the relevant
  precancer atlas (integrative analysis of 128 datasets from 62 participants;
  conventional adenomas, serrated polyps and CRC counterparts); Heiser et al.
  2023 has 31 colorectal specimens with spatial multiomics and is mainly a CRC
  regional-heterogeneity resource. Do not call the latter a normal-to-polyp-to-
  cancer validation cohort without an audited pathology table.
- Validation decision: make Chen L3/L4 scRNA the discovery/core dataset, reserve
  its independent discovery/validation split for internal replication, use MxIF
  and Visium to confirm the location and marker expression of pre-specified
  states, and use Stanford GSE201348 for external normal-to-polyp-to-CRC program
  transfer (stratifying FAP status). GSE132465 is an additional normal-versus-CRC
  endpoint validation only.

## 2026-09-17 — public CELLxGENE access verified

- Queried CELLxGENE's public collection API for the Chen et al. Vanderbilt
  collection, without credentials. It exposes three direct H5AD assets and all
  returned HTTP 200 to a metadata-only HEAD request:
  - Discovery epithelial: 65,088 cells, 30 listed donors, 1.52 GB —
    `https://datasets.cellxgene.cziscience.com/9da034b0-de48-47ab-97f6-21b5f2dbd1a4.h5ad`
  - Validation epithelial: 57,723 cells, 26 listed donors, 1.15 GB —
    `https://datasets.cellxgene.cziscience.com/6f8f0b95-3779-4c0e-824d-4810c39f008c.h5ad`
  - Combined discovery/validation non-epithelial: 10,696 cells, 144 MB —
    `https://datasets.cellxgene.cziscience.com/91a55470-7520-4ecf-bcbc-1062f7ef4cdb.h5ad`
- The collection description reports 128 independent scRNA datasets from 62
  tumours; its declared diseases include normal, hyperplastic polyp, sessile
  serrated adenoma/polyp, tubular adenoma, tubulovillous adenoma and colorectal
  cancer. Tissue coverage includes ascending, transverse, descending, sigmoid
  colon, hepatic flexure/cecum and rectum. The abnormal-cell component includes
  seven fresh CRCs (two MSI-H and five MSS). The 30+26 epithelial donor lists
  overlap (for example HTA11_866), so they must not be summed as 56 independent
  people without a deduplicated join.
- For spatial/MxIF files, use HTAN Phase 1 Explore and filter Atlas = HTAN
  Vanderbilt, then assay/level; public Synapse downloads may require a free
  Synapse login but not dbGaP approval. Do not use direct data URLs copied from
  an expired session; obtain a fresh manifest after logging in.

## 2026-09-17 — direct cluster download submitted

- At the user's request, created `scripts/download_vanderbilt_cellxgene.sh` and
  submitted Slurm job `256252`. It downloads the three verified public CELLxGENE
  H5AD files (about 2.8 GB) to
  `/l/users/yuqi.lei/HTA11/data/vanderbilt_cellxgene/`, avoiding a user-mediated
  local download/upload. The script validates each expected byte size, resumes a
  retained partial file after an interruption, atomically renames complete files,
  and prints SHA-256 checksums.
- First submission was rejected because the inherited default `long` partition
  accepts GPU-only QoS values. Inspected the scheduler and changed the I/O job to
  `cscc-cpu-p` with QoS `cscc-cpu-qos`; no debug or exclusive resources requested.
  The corrected job was accepted and observed running on `cn-02`.
- Do not start analysis until completion and a light H5AD integrity/metadata load
  is performed on Slurm. Current running status is in `ONGOING.md`.

## 2026-09-17 — team working roadmap

- User identified the team as Yuqi Lei and Muhammed Bah and requested a concise,
  intentionally changeable roadmap. Added `ROADMAP.md` as an internal operational
  plan, not text for either student's individual submission.
- It constrains the project to an RNA-first, donor-aware, cross-sectional study
  of normal-to-conventional-adenoma-to-CRC cell-state changes; serrated lesions
  remain a separate analysis if metadata permit. Spatial validation is optional
  and drops before the core if it jeopardizes delivery. Initial flexible role
  split: Yuqi leads curation/QC/annotation and Muhammed leads inference/validation,
  with mutual review.

## 2026-09-17 — roadmap narrative revision

- User requested removal of defensive wording from the internal roadmap. Recast
  `ROADMAP.md` as a positive scientific narrative: a focused map of cell-state
  programs and tissue composition accompanying colorectal neoplastic
  transformation. Methodological boundaries remain as design choices—public
  RNA-first data, donor/specimen replication, independent validation and a
  separate serrated route—rather than self-limiting claims.

## 2026-09-17 — Stanford access audit completed and interpretation corrected

- Finished the full public GEO/ENA inventory and bounded retries. Preserve
  initial failures and intermediate summaries rather than overwrite them.
- Correction to a transport-only interpretation: HTTP 206 plus two transferred
  bytes can still be HTML or an unexpectedly short object. Added content-type,
  byte-range and ENA expected-size validation to the summarizer; three ATAC
  exports remain unverified despite successful HTTP transport. Results and exact
  filenames are in the [weekly report](09_18_report.md) and record 003.
- Conclusion: processed Stanford RNA and ATAC access is established at every
  listed component; bulk DNA and complete raw-read reprocessing are not assured.
  This supports an RNA cell-state workflow without reversing the user's DNA
  availability constraint or changing the chosen discovery/validation roles.
- No full sequencing downloads, compute jobs, authentication changes or access
  restriction bypasses. Five small validation assertions and script syntax
  checks passed. Next scientific gate remains full-file load/QC under Slurm and
  an audited donor-by-stage design, not raw FASTQ alignment.

## 2026-09-17 — focused roadmap brainstorming and spatial feasibility

- User asked to ground the normal-to-cancer cell/gene/spatial question and
  clarified that “race types” means disease/polyp subtypes, not ethnicity.
  Recommended a human colorectal conventional-route comparison: normal/
  non-neoplastic mucosa, pooled TA/TVA and documented MSS adenocarcinoma.
  This is a recommendation pending team selection. Preserve TA/TVA, site and
  normal-source metadata; keep serrated lesions and MSI-H outside the primary
  contrast. Subtype labels do not prove precursor lineage.
- Translate “contribute most” into separate measurable quantities: epithelial
  state abundance, within-state expression/program changes, and regional spatial
  localization. A hypothesis needs an expected direction and a contradictory
  observation; candidate expectations belong to brainstorming, not project results.
- Checked Chen 2021 and Heiser 2023 primary articles. Correction/clarification to
  the earlier spatial discussion: the Heiser cohort includes pre-cancer and
  normal tissue (four TA/TVA, four SSL/HP, one normal, twelve MSS CRC, ten MSI-H
  CRC). Thus an adenoma/cancer spatial comparison is a candidate, while a single
  normal supports a descriptive reference only. Actual access and per-assay
  replication still require audit. Evidence and sources are in record 004.
- Re-fetched the public CELLxGENE API and preserved the response. Collection text
  mentions an Abnormal/CRC dataset that is not separately exposed among its
  three current assets. Broad disease labels do not establish exact CRC/MSI
  coverage; H5AD observations and specimen metadata must resolve it. Earlier
  observed DIS/VAL donor overlap also prevents assuming donor independence.
- Updated the internal plan's order: check spatial feasibility in Week 1 and
  reserve Weeks 6–7 for a single spatial assay if spatial organization stays in
  the main question. This supersedes treating all spatial work as an optional
  Week 9 addition. If the spatial gate fails, explicitly revise the question.
  More cohorts, a second spatial assay, trajectories and ML remain extensions.
- Kept the assignment boundary explicit: internal AI-assisted notes/worksheet
  support brainstorming; each team member independently composes and manually
  types all six submitted answers. No completed assignment answers or submission
  were generated. No H5AD load, new Slurm job or biological analysis in this review.

## 2026-09-17 — GitHub update preparation

- User requested publishing the current project updates to the existing
  `CyclopsRay/WhatsTheCancerType` repository. Reviewed the roadmap, worksheet,
  scope notes, access-audit evidence/scripts and weekly records together; added
  README links to the current planning documents.
- Fetched `origin`; remote `main` matches the local starting commit `f3359bc`.
  JSON/JSONL parsing, Python syntax, Bash syntax and diff whitespace checks passed.
  The reviewed file set contains small documentation, scripts and provenance
  outputs; downloaded source caches, sequencing matrices and job logs are excluded.
- Publish as an ordinary commit and fast-forward push, then verify remote `main`
  against local HEAD. The terminal and final response record that verification;
  this preparation entry does not claim a completed push.
