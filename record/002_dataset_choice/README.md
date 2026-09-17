# 002 — Dataset choice under DNA-access constraints

Date: 2026-09-17. Status: research advice and feasibility evidence, not a student
submission. The user confirmed a ten-week project and a preference for studying
normal-to-adenoma-to-cancer cell-state changes. Team names and any mandatory
multimodal/ML requirement have not been supplied.

Follow-up: the [per-file access audit](../003_stanford_access/README.md) supersedes
the initial header-only checks below. All processed RNA and ATAC files passed
anonymous range requests, with representative content-format checks. Full-file
integrity, complete original barcode reads and WGS access are separate questions.

## Constraints to retain

- User reports HTA11 Bulk DNA Level 3 unavailable for governance reasons. Treat
  it as unavailable regardless of the portal's open-access label. No attempt was
  made to bypass access restrictions or obtain equivalent controlled files.
- [Availability snapshot](availability_snapshot.tsv) transcribes the supplied
  screenshot. Source attachment: `codex-clipboard-43e7125a-709c-4b40-b91c-6d85d94ab60c.png`,
  received 2026-09-17. The screenshot has no visible page URL or capture date.
- Counts describe files, not independent patients, tissues, cells, or matched
  multiomic observations. They are not specific proof that every file belongs
  to the Islam et al. 2024 publication.
- RNA matrices support expression and composition analyses. They do not contain
  the sequence reads required for somatic variant calling and cannot replace DNA
  evidence for founder-clone reconstruction. RNA-derived copy-number estimates
  would also not establish multiple normal founders.
- The assignment allows brainstorming with AI but requires each of two team
  members to compose and type their own submission. The project plan and worksheet
  support that process; neither is submission-ready text.

## Dataset recommendation

Use **Stanford/Becker et al. as the working primary candidate**, with an RNA-only
core and external CRC endpoint validation. This is a better match to the user's
preferred comparison than making restricted DNA recovery the critical path.
The recommendation is not a claim that the full dataset has already passed QC.

| Candidate | Evidence | Role and caveat |
|---|---|---|
| HTAN Vanderbilt / HTA11 | Existing paper review; screenshot lists RNA, spatial and imaging files | Keep as reference or optional extension; matching normal/adenoma/CRC RNA inventory and actual access remain unverified |
| HTAN Stanford / HuBMAP, Becker et al. 2022 | Study includes 48 polyps, 27 normal/unaffected tissues and 6 CRCs across assays; RNA subseries GSE201348 lists 72 GEO sample entries | Primary candidate for stage-associated epithelial states; study-wide totals are not the RNA subset or donor count; substantial FAP component |
| GEO GSE132465, Lee et al. 2020 | 63,689 cells; 23 CRC patients; 23 primary tumour and 10 matched normal specimens; UMI counts and cell annotations listed | Independent validation of normal-versus-CRC expression direction, not of the adenoma transition |

Primary sources: [Becker et al.](https://www.nature.com/articles/s41588-022-01088-x),
[GSE201348](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE201348),
[GSE132465](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE132465).
The Stanford assay uses single-nucleus RNA; the companion assay is scATAC-seq.
These assays must not be described as measurements in the same cells without
checking correspondence. The study spans HTAN and HuBMAP, so the GEO mirror is
useful for retrieving the published cohort together.

## Access evidence and first-week acceptance criteria

[Access checks](access_checks.tsv) returned HTTP 200 for the Stanford RNA matrix
archive and the external validation count/annotation endpoints. These were HEAD
requests, not full downloads. GEO lists the Stanford processed MTX/TSV archive at
about 1.2 GB; `RAW.tar` is its filename, not evidence that it contains FASTQ reads.

Before freezing the analysis cohort:

1. Download processed counts and small metadata to approved persistent storage;
   load on Slurm and verify dimensions, gene identifiers, and barcode mappings.
2. Map every library to tissue, donor, pathology, bowel location, assay and batch.
   Distinguish healthy normal from histologically unaffected FAP tissue.
3. Count independent donors by pathology and quantify missingness. Repeated
   polyps from one donor are not independent biological replicates.
4. Check whether stage and donor/FAP status are confounded. A covariate cannot
   correct a contrast with no overlap. Prioritize within-FAP unaffected-versus-
   adenoma comparisons where supported; treat sparse CRC contrasts cautiously.
5. Inspect the design matrix and biological replication before inferential tests.
   If the full stage comparison is not estimable, reduce scope explicitly rather
   than treating thousands of cells as replication.

## Scientific scope for brainstorming

- Focus: epithelial stem-like versus differentiated states and their gene programs.
- Comparisons: unaffected/normal versus adenoma; adenoma versus CRC, where supported.
- Added value: donor-aware reproducibility and cross-study transfer, beyond
  recreating a UMAP or the published ordering.
- Main outputs: donor-by-stage inventory, sample-level cell-state proportions,
  gene/pathway effects with uncertainty, and independent CRC endpoint validation.
- Interpretation: cross-sectional stage-associated differences. These observations
  cannot prove that a sampled adenoma later becomes a sampled cancer or predict
  which polyp will progress clinically. Healthy and unaffected-FAP samples are
  distinct comparison groups; serrated lesions are a separate pathway.

Use RNA alone for the deliverable. ATAC can be an extension only after the core
is working and if a second modality is required or time permits. Keep genetic
clonality, longitudinal progression prediction, and a multi-cancer classifier
outside the core scope.

## Analysis notes

Use Seurat for sparse count import, QC and annotation; preserve integer counts
for differential expression. Confirm annotations with markers independently of
stage comparisons. Analyze both cell-state abundance and expression within
comparable states so their effects are distinguishable.

Aggregate counts by specimen and cell type/state. For repeated specimens, use
donor-aware models or a justified donor aggregation; never treat cells or polyps
from one person as independent donors. Candidate tools are edgeR quasi-likelihood
models where the design is estimable, or limma-voom with donor blocking for
appropriate repeated measures. Biological replication is essential; see
[Squair et al.](https://www.nature.com/articles/s41467-021-25960-2).
Use ranked pathway enrichment (fgsea), effect sizes and multiple-testing correction.

Check sensitivity to donor exclusion, tissue location, FAP status, cell yield and
cell-cycle programs. Compare corrected and uncorrected visualizations; use counts,
not integrated expression values, for count-based tests. Validate fixed pathway
directions separately in GSE132465; do not merge cohorts and confuse study effects
with progression. Differences between nuclei and whole cells also affect transfer.

Optional trajectory analysis is descriptive and should not be used as evidence
of lineage or elapsed time. If added, restrict to comparable epithelial lineages
and assess sensitivity to roots and donor composition. A predictive ML model is
not required by the information currently provided; if used, all fitting and
feature selection must be inside donor-disjoint training folds.

## Planning artifacts

- [Ten-week operational plan](../../PLAN.md)
- [Personal writing worksheet](../../ROADMAP_WORKSHEET.md)
- [Weekly decision record](../../report/09_18_record.md)

No matrix downloads, analysis jobs, or assignment submissions were performed in
this feasibility review.
