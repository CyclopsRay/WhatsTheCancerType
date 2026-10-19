# Project plan

## Completed foundation

- First paper record, public-supplement retrieval, and metadata-audit scripts.
  Evidence and decisions are in `report/09_18_report.md` and `report/09_18_record.md`.
- Git initialization and GitHub remote setup for `CyclopsRay/WhatsTheCancerType`.

## Current scope — ten weeks

**Revised 2026-09-18** against the audited open-access release
([record 005](record/005_open_access_audit/README.md)). The concise,
change-controlled statement is [ROADMAP.md](ROADMAP.md); this file holds the
schedule and the gates.

Primary: the public Vanderbilt/HTA11 scRNA Level-4 objects. Main contrast is
**within-donor polyp versus that donor's own normal mucosa**, conditioned on
**route**. Paired-donor counts measured in the data we hold: conventional 19
donors, serrated 15 donors (the 28 / 21 quoted earlier are full-release figures
needing the Synapse-only objects, currently blocked). Driver genotype from the 253 open exome VCFs (85 donors shared with
scRNA) is a **droppable extension**, gated on a Week-1 usability spot-check.

Removed from the main contrast: the three-stage normal -> adenoma -> carcinoma
framing. The open release has 7 CRC specimens at Level 4 with 3 donor pairs.
CRC is retained only as a declared underpowered direction check.

**Revised 2026-10-19:** spatial is now **Visium-first** — the OSF MxIF quantification
tables are empty files, so MxIF is dropped (see `KNOWLEDGE.md`). The paragraph below
is the superseded 2026-09-18 reasoning.

Spatial was **MxIF-first**, not Visium-first. MxIF covers 28 polyp specimens and
shares 32 donors with scRNA; Visium has 7 polyp captures and shares 10 donors.
The OSF deposit (`osf.io/hftq2`, anonymous) supplies 16 pre-segmented MxIF
threshold quantification tables, which is what makes the MxIF arm affordable.
Visium polyp captures remain an illustrative endpoint.

Stanford GSE201348 drops from the plan as an external-support cohort — the
within-donor paired design is internal to HTA11 and Stanford cannot replicate it.
The Stanford access audits in `record/002_dataset_choice/` and
`record/003_stanford_access/` are retained as historical evidence.

DNA is no longer recorded as unavailable; see the correction in `KNOWLEDGE.md`.
No raw Level 1/2 sequencing and no dbGaP request is required for anything above.

## Status at 2026-10-19 (instructor feedback: feasibility)

Core pipeline steps of weeks 2–6 and the Visium endpoint have a first working run
(record 006). What remains is depth and robustness, not new methods:

1. Marker check of `Cell_Type`; mito/QC decision; pooled DIS+VAL fit.
2. Separate composition from expression: within-state route split; lesion-state
   contrasts (ASC vs normal STM/TAC, SSC likewise).
3. Sensitivity: HP vs SSL, site, leave-one-donor-out; score published NMF k=30 programs.
4. Visium on all 7 sections with section as the unit.
5. Optional after the core: OT correspondence (`moscot`).

## Milestones

| Weeks | Work and candidate tools | Completion evidence |
|---|---|---|
| 1 | Load the three downloaded H5ADs on Slurm; join `obs` to HTAN biospecimen IDs; build donor x pathology x site x batch table; retrieve the three non-CELLxGENE Level-4 objects and the OSF MxIF/NMF/WES derivatives; spot-check 3–5 exome VCFs | Donor-by-pathology inventory from matrix contents; paired-donor list; spatial input inventory; scope freeze; genotype extension kept or dropped |
| 2 | Scanpy/Seurat sparse import, assay-appropriate QC, label completeness | QC report; exclusion log; reproducible count objects |
| 3 | Epithelial state annotation with reference labels and independent markers; batch inspection | Annotated states with donor and route coverage per state |
| 4 | Within-donor state composition, polyp vs own normal, fitted per route | Paired abundance effects with uncertainty; composition-vs-state distinction |
| 5 | Specimen x state pseudobulk; edgeR or limma-voom with donor in the design; fgsea; score the published k=30 NMF spectra | Per-route effect tables, FDR, fixed program candidates |
| 6 | Shared vs route-specific decomposition; donor-consistency counts per program; optional unbalanced-OT state correspondence (`moscot`, fallback scVI/Harmony nearest-neighbour or label transfer) | The comparative answer, with counts not only p-values; evidence on whether polyp states are new or redistributed |
| 7 | MxIF endpoint from OSF quantification tables; Visium polyp captures as illustration | Regional effect estimates per specimen; descriptive Visium panels |
| 8 | Donor-disjoint replication of fixed contrasts; CRC direction check labelled underpowered | Reproducibility evidence with overlap stated |
| 9 | Donor-exclusion, site, cell-yield, cell-cycle sensitivity; genotype extension if it survived | Robustness summary; final core figures |
| 10 | Reproduce from scripts, audit provenance, interpret limits, presentation | Reproducible code, figures, dataset inventory, course deliverables |

Large imports, QC, normalization, model fitting and plots on full matrices run
through Slurm. Store datasets and environments outside the home directory.

## Decision gates and interpretation

- **Cohort gate (Week 1).** Every cohort number now on record is portal metadata.
  If `obs` cannot be joined to pathology and donor, the paired design fails and
  the project reverts to a between-donor contrast, stated as such.
- **Genotype gate (Week 1).** The 253 VCFs are `MAP.*_polyp.rmdup.indel.recal-
  filtered.vcf` — GATK germline-style, no matched-normal token. No usable somatic
  calls means the extension is dropped and the drop is recorded.
- **Spatial gate (Week 1).** If OSF MxIF quantification does not cover polyp
  specimens overlapping our scRNA donors, fall back to the 7 Visium polyp
  captures and state that the spatial claim is descriptive.
- Do not equate cells, files, specimens and donors. The replication unit is the
  donor; specimens are nested within donors and several donors contribute more
  than one polyp.
- Route and anatomical site are entangled (serrated lesions are proximal). Report
  the crossing where the site field permits; do not present a route effect as if
  site were controlled unless it was.
- Only 3 donors carry both routes, so the route comparison is between donors.
  Say so rather than implying a within-donor route contrast.
- HP/atypia pooled with SSL as "serrated" buys 17 donors; keep the unpooled
  result as a sensitivity check either way.
- Keep the core independent of raw FASTQ alignment and deep learning.
- Cross-sectional state ordering is not observed ancestry; no founder clonality
  or clinical progression probability follows from this design. An optimal-
  transport coupling between normal and polyp cells is a transcriptional
  correspondence, not a lineage map — it must not be given directional language.
- The OT correspondence is optional and first in the drop order. The pseudobulk
  differential expression must stand without it. Couplings are sensitive to the
  cost metric and the unbalancedness parameter; check with leave-donor-out over
  the 19 paired donors.
- Yuqi Lei initially leads retrieval/QC/annotation; Muhammed Bah initially leads
  the paired design and inference; both review metadata joins and statistics.
  Roles are flexible; see `ROADMAP.md`.

## Remaining choices

- Final question in each student's own words.
- Whether HP pools with SSL in the primary route definition.
- Whether the course requires a second modality or a predictive-ML component.
- Pinned analysis environment, persistent data path and Slurm resource profile.
- Exact donor and specimen subset after the Week 1 `obs` audit.
