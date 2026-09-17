# HTA11 working roadmap

**AI-assisted internal planning only; not either student's submission.**
The latest [scope and feasibility notes](record/004_roadmap_scope/README.md)
refine the proposed subtypes and spatial objective. Follow the updated schedule
in [PLAN.md](PLAN.md): a main spatial question requires a Week 1 spatial-data gate.

**Team:** Yuqi Lei and Muhammed Bah

**Status:** working plan, deliberately simple and subject to change after the
Week 1 metadata audit.

## Goal

Chart the cell-state programs and tissue composition that distinguish normal
colon, conventional adenoma and colorectal cancer in public Vanderbilt
single-cell RNA data. This creates a focused map of the cellular programs that
accompany colorectal neoplastic transformation. Serrated lesions form a parallel
biological route when their metadata support a well-powered analysis.

All findings will be expressed as stage-associated patterns across human
specimens, providing a clear and reproducible view of the transition landscape.

## Minimum viable project

1. Build an audited donor/specimen/pathology table for the public Vanderbilt
   discovery and validation scRNA objects.
2. Identify comparable epithelial states using established markers and reference
   labels.
3. Test stage-associated changes in state abundance and within-state expression,
   using specimen/donor rather than cells as replication.
4. Replicate fixed findings in donor-disjoint Vanderbilt subsets where supported,
   or an audited external cohort such as Stanford GSE201348.
5. For the proposed spatial main question, quantify localization in an accessible
   spatial assay; verify feasibility in Week 1 and use the schedule in `PLAN.md`.

**Success means** a compact, reproducible set of cell-state and pathway changes
that explains how the colorectal tissue ecosystem is reorganized across stages.

## Data strategy

| Role | Data | Contribution |
|---|---|---|
| Core discovery | Vanderbilt DIS epithelial scRNA | Establish stage-associated epithelial states and programs |
| Internal replication | Vanderbilt VAL epithelial scRNA | Test discovery-fixed results after auditing donor overlap and pathology coverage |
| Microenvironment context | Vanderbilt combined non-epithelial scRNA | Place epithelial changes in immune and stromal context |
| Spatial support | Vanderbilt MxIF and Visium | Localize selected states and markers in tissue architecture |
| External support | Stanford GSE201348 | Assess transfer of fixed programs across a second cohort |

The analytical foundation is a public RNA-first resource. Specimens and donors
provide the biological replication for all statistical comparisons.

## Roles (flexible)

| Area | Initial lead | Cross-check |
|---|---|---|
| Cohort table, file provenance, reproducible data loading | Yuqi | Muhammed reviews joins and exclusions |
| QC, cell-state annotation, marker checks | Yuqi | Muhammed checks biological labels |
| Statistical design, pseudobulk, abundance and pathway tests | Muhammed | Yuqi checks replication unit and code |
| Validation, figures and interpretation | Shared | Both approve every final claim |

Roles can evolve as the data and each team member's strengths become clearer.

## Ten-week sequence

| Week | Deliverable | Focus |
|---|---|---|
| 1 | Load public H5ADs; donor/pathology/overlap tables; spatial-access gate | Freeze supported RNA contrasts and a spatial endpoint |
| 2 | QC record and epithelial labels | Build a traceable, biologically interpretable cohort |
| 3 | State abundance by specimen/donor | Resolve compositional remodeling across stages |
| 4–5 | Pseudobulk expression and pathway results | Identify donor-supported programs within comparable states |
| 6–7 | Spatial localization using the selected assay | Quantify regional distribution of fixed RNA programs or measured markers |
| 8 | Replicate supported contrasts | Use donor-disjoint internal subsets or an audited external cohort |
| 9 | Sensitivity checks and evidence consolidation | Assess donor, site, cell-yield and cell-cycle dependence |
| 10 | Reproduce, audit, figures, presentation | Deliver a coherent and reusable study resource |

## Roadmap adaptation

The Week 1 metadata audit will set the exact stage contrast and final cohort.
Spatial work is required if spatial organization remains in the main question;
failure of its access/design gate means explicitly revising the question to RNA
outcomes. Additional modalities and cohorts follow after the selected core.
