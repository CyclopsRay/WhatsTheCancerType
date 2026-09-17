# Project plan

## Completed foundation

- First paper record, public-supplement retrieval, and metadata-audit scripts.
  Evidence and decisions are in `report/09_18_report.md` and `report/09_18_record.md`.
- Git initialization and GitHub remote setup for `CyclopsRay/WhatsTheCancerType`.

## Current scope — ten weeks

User preference: normal-to-adenoma-to-cancer cell-state changes. The working
primary is now the public Vanderbilt/Chen et al. discovery and validation scRNA
objects, with Stanford/Becker GSE201348 as external support if the metadata permit.
Final selection depends on the Week 1 metadata/load gate. DNA is unavailable and
outside the required scope. See the concise, change-controlled [working roadmap](ROADMAP.md).
Latest [brainstorming and evidence](record/004_roadmap_scope/README.md) propose
human colorectal normal/non-neoplastic mucosa, conventional TA/TVA and documented
MSS adenocarcinoma, with epithelial programs as the main focus. The user clarified
that subtypes, not patient ethnicity, were intended. This is a proposed cohort,
not a completed metadata selection or student-authored assignment.

Access update 2026-09-17: every deposited processed RNA/ATAC file passed a bounded
anonymous GET test; representative content formats were verified. See
`record/003_stanford_access/`. The remaining Week 1 gate is full-file loading,
QC and an identifiable donor/stage design. Bulk WGS remains unverified.
The raw-export audit passed all 72 RNA FASTQs but found three ATAC FASTQ
content/size exceptions (175/178 passed). Keep raw reprocessing outside the
critical path; resolve these and original 10x read completeness only if needed.

Core: epithelial cell states, sample-level abundance, within-state expression,
pathway interpretation and donor-aware robustness. Because the proposed question
includes spatial organization, one usable spatial assay (Visium or MxIF) must
pass the Week 1 access/design gate. If it fails, revise the question explicitly
to the RNA scope. A second spatial assay and scATAC remain optional. See
[design notes](record/002_dataset_choice/README.md).

## Tonight — 2026-09-17

1. Team (Yuqi Lei and Muhammed Bah) confirms dataset proposal, focused comparison,
   and division of work.
2. Check course requirements for multiple modalities or predictive ML.
3. Each member independently writes and types the six answers using the
   [worksheet](ROADMAP_WORKSHEET.md) and primary sources, then submits through
   the course system. No AI-generated submission prose or automated submission.

## Milestones

| Weeks | Work and candidate tools | Completion evidence |
|---|---|---|
| 1 | Audit downloaded RNA counts/metadata and exact CRC availability; map donor, specimen, pathology, MSI, site and batch; audit spatial access, regions and markers; pin environment | Donor-by-pathology inventory; donor-overlap table; usable RNA and spatial inputs; scope freeze |
| 2 | Seurat sparse import and assay-appropriate QC; inspect library quality and label completeness | QC report; exclusion log; reproducible count objects |
| 3 | Epithelial annotation with reference labels and independent markers; inspect cohort/batch effects | Annotated epithelial states and donor coverage per state |
| 4 | Sample-level cell-state composition and within-donor comparisons where possible | Abundance effect estimates and uncertainty; composition-versus-state distinction |
| 5 | Specimen-by-state pseudobulk; edgeR or limma-voom with donor-aware design; fgsea pathway enrichment | Pathology contrast effects, FDR tables and fixed program candidates |
| 6–7 | Map fixed programs/markers onto the selected spatial assay; compare histology regions; summarize per specimen | Spatial maps and regional effect estimates; normal reference shown descriptively if only one normal specimen |
| 8 | Replicate fixed RNA contrasts using donor-disjoint subsets where available; otherwise use an audited external cohort | Reproducibility evidence with overlap and contrast coverage stated |
| 9 | Donor-exclusion, site, cell-yield and cell-cycle sensitivity; consolidate RNA/spatial evidence | Robustness summary, final core figures and interpretation |
| 10 | Reproduce from scripts, audit provenance, interpret limits, prepare presentation and personal writing | Reproducible code, figures, dataset inventory and completed course deliverables |

Large imports, QC, normalization, model fitting and plots on full matrices run
through Slurm. Store datasets and environments outside the home directory.

## Decision gates and interpretation

- Confirm sufficient independent donors and an identifiable design; do not equate
  cells, files, polyps, and donors. Healthy controls and unaffected-FAP tissues
  remain distinguishable. Account for repeated specimens from a person.
- Audit DIS/VAL donor overlap before calling replication independent. Verify
  exact CRC pathology/MSI labels in the actual RNA objects rather than assuming
  collection-level descriptions establish a three-stage dataset.
- The proposed spatial source has one normal specimen, four TA/TVA and twelve
  MSS CRCs at publication level. Use the normal as a descriptive reference;
  prioritize replicated adenoma/cancer or within-specimen regional comparisons.
  Audit patient overlap before interpreting multimodal support as external validation.
- If adenoma-to-CRC is confounded or underpowered, prioritize a supported
  unaffected-to-adenoma comparison and describe CRC validation separately.
- GSE132465 lacks adenomas; it cannot replace the whole progression study without
  changing the research question. If the primary fails, explicitly revisit scope.
- Keep core independent of DNA, raw FASTQ alignment and deep learning. One spatial
  assay is required for a spatial main question; otherwise revise that question.
  Do not infer founder clonality or clinical progression probability.
- Cell-state ordering is cross-sectional; a trajectory is not observed ancestry.
- Yuqi Lei initially leads curation/QC/annotation; Muhammed Bah initially leads
  inference/validation; both review metadata joins and donor-aware statistics.
  These roles are flexible; see `ROADMAP.md`.

## Remaining choices

- Final question in each student's own words.
- Team selection of the proposed conventional TA/TVA and MSS endpoint scope;
  exact spatial measurement after the access/annotation gate.
- Whether the course requires multiple modalities or predictive ML.
- Persistent data path, pinned analysis environment and Slurm resource profile.
- Exact donor and specimen subset after Week 1 audit.
