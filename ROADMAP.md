# Roadmap

**Team:** Yuqi Lei and Muhammed Bah

**Status:** revised 2026-09-18 against the audited HTA11 open-access release.
Cohort numbers below come from the HTAN release manifest
([record 005](record/005_open_access_audit/README.md)), not from a portal browse.
The `obs` audit of 2026-09-18 has since replaced the portal counts for the three
objects we hold; both sets are shown below because they differ.

## Goal

Characterize the epithelial transcriptional programs that separate a colorectal
polyp from **normal mucosa of the same donor**, and determine how much of that
program is common to both routes into neoplasia versus specific to one of them.

Working question, for each student to rewrite in their own words:

> Which epithelial transcriptional programs distinguish colorectal polyps from
> matched normal mucosa of the same donor, how much of that program is shared
> between the conventional (TA/TVA) and serrated (SSL/HP) routes versus specific
> to one of them, and how consistently does it hold across donors and in tissue
> context?

Everything is cross-sectional and stage-*associated*. Nothing here observes a
cell becoming neoplastic, and no causal or lineage claim follows from it.

## Why this shape and not the previous one

The earlier draft made normal -> adenoma -> carcinoma the main contrast. The open
release does not support that. Donor counts in the scRNA Level-4 release:

| Group | Full release, donors | Full release, paired | **Held (DIS+VAL), paired** |
|---|---|---|---|
| Normal | 59 | — | 43 donors |
| Conventional (AD) | 53 | 28 | **19 donors** |
| Serrated (SER) | 38 | 21 | **15 donors** |
| Carcinoma (UNC) | 7 | 3 | 5 donors |

The right-hand column is what the three downloaded objects actually contain
(121 specimens, 55 donors). The full-release column needs the three Synapse-only
Level-4 objects, currently blocked by a governance issue. **Plan against 19 and
15**; treat 28 and 21 as upside if Synapse opens.

Normal-to-polyp is paired and donor-replicated. Polyp-to-carcinoma is seven
specimens with essentially no pairing. CRC therefore moves out of the main
contrast and becomes a declared underpowered direction check.

The conditioning axis — the "under which circumstances" — is the **route**. That
is what distinguishes this from a plain differential-expression list, which the
source paper already published.

## Design

- **Replication unit: the donor.** Never the cell. Cells within a specimen are
  pseudo-replicates; specimens within a donor are nested.
- **Primary contrast: within-donor**, polyp versus that donor's own normal
  mucosa. This removes donor background from the comparison and is the reason
  the paired sets (19 and 15 donors) matter more than the raw specimen totals.
- **Conditioning: route.** Fit the normal->polyp effect separately in the
  conventional and serrated donor sets, then quantify shared versus
  route-specific programs rather than reporting two unconnected gene lists.
  Only 3 donors carry both routes, so the route comparison is between donors and
  is reported as such.
- **Extension: driver genotype.** 85 donors are shared between the scRNA release
  and the 253 open exome VCFs. If those VCFs yield usable per-polyp APC / KRAS /
  BRAF calls, test whether route-specific programs track genotype rather than
  histology. **Droppable without changing the main question.**
- **Confounders to report, not to assume away:** anatomical site (serrated
  lesions are proximal, so site and route are entangled), donor, sequencing
  batch, cell yield, cell cycle.

## Data strategy — all open access, no dbGaP request

| Role | Data | Access | Contribution |
|---|---|---|---|
| Core | scRNA Level 4 H5ADs — **held: DIS+VAL epithelial, 121 specimens, 55 donors**; 3 further objects on Synapse | CELLxGENE (held) / Synapse (blocked) | Epithelial states and programs; the paired contrast |
| Core backup | scRNA Level 3 matrices (364 files, 130 donors) | Synapse | Recoverable counts if a Level-4 object lacks needed labels |
| Spatial | MxIF Level 2 (46 specimens, 45 donors, 28 polyps; **32 donors shared with scRNA**) | CRDC-GC open | Localize fixed programs and markers in tissue |
| Spatial shortcut | OSF `MxIF/quantification/` — 16 pre-segmented threshold cell tables | osf.io/hftq2, anonymous | Removes whole-slide segmentation from the critical path |
| Spatial illustration | Visium Level 4, **7 polyp captures** of 43; 10 donors shared with scRNA | Synapse | Descriptive localization only — not the powered endpoint |
| Extension | Bulk DNA Level 3, 253 exome VCFs, 85 donors shared with scRNA | Synapse | Per-polyp driver genotype, if the calls prove usable |
| Reference | OSF `scRNA/VUMC_NMF/` published k=30 gene spectra | osf.io/hftq2 | Fixed external program definitions to score against |

Level 1/2 raw sequencing is behind a dbGaP request and is **not used**.

## Minimum viable project

1. Audited donor / specimen / pathology table built from the H5AD `obs`, joined
   to HTAN biospecimen IDs — not from portal metadata alone.
2. Comparable epithelial states across specimens, using established markers plus
   the published reference labels.
3. Within-donor polyp-versus-normal effects on state abundance and on
   within-state pseudobulk expression, fitted separately per route.
4. Shared-versus-route-specific decomposition of those effects, with donor
   consistency reported as a count, not only as a p-value.
5. One spatial endpoint on MxIF quantifying where the fixed programs or their
   marker proxies sit in tissue.

**Success:** a compact, reproducible set of epithelial program changes with an
explicit statement of which are generic to polyp formation and which belong to
one route — plus an honest account of what the design cannot establish.

## Roles (flexible)

| Area | Initial lead | Cross-check |
|---|---|---|
| Retrieval, cohort table, provenance, reproducible loading | Yuqi | Muhammed reviews joins and exclusions |
| QC, epithelial state annotation, marker checks | Yuqi | Muhammed checks biological labels |
| Paired design, pseudobulk, abundance and pathway tests | Muhammed | Yuqi checks replication unit and code |
| Spatial arm, WES extension, figures, interpretation | Shared | Both approve every final claim |

## Ten-week sequence

| Week | Deliverable | Focus |
|---|---|---|
| 1 | H5AD `obs` audit; donor x pathology x site table; Synapse and OSF retrieval; VCF spot-check | Freeze the cohort and decide whether the genotype extension survives |
| 2 | QC record, exclusion log, reproducible count objects | Traceable cohort |
| 3 | Epithelial states with reference labels and independent markers | Comparable states across donors and routes |
| 4 | Within-donor state abundance, per route | Compositional remodeling, paired |
| 5 | Specimen x state pseudobulk; edgeR/limma-voom with donor in the design; fgsea | Program candidates, per route, with FDR |
| 6 | Shared vs route-specific decomposition; donor-consistency counts; optional unbalanced-OT correspondence between normal and polyp states | The answer to the second clause, plus whether polyp states are new or redistributed |
| 7 | MxIF spatial endpoint from OSF quantification tables; Visium polyp captures as illustration | Tissue context for the fixed programs |
| 8 | Replication in donor-disjoint subsets; CRC direction check (declared underpowered) | Does it hold outside the discovery donors |
| 9 | Sensitivity: donor exclusion, site, cell yield, cell cycle; genotype extension if it survived Week 1 | Robustness |
| 10 | Reproduce from scripts, audit provenance, figures, presentation | Deliverables |

## Gates and what gets dropped first

- **Week 1 cohort gate.** If the H5AD `obs` cannot be joined to pathology and
  donor, the paired design fails and the project reverts to a between-donor
  normal-versus-polyp contrast, stated as such.
- **Week 1 VCF gate.** The 253 VCFs are named GATK-germline-style with no
  matched-normal token. If a spot-check shows no usable somatic calls, the
  genotype extension is dropped and recorded as dropped.
- **Week 1 spatial gate.** If the OSF MxIF quantification tables do not cover
  polyp specimens that overlap our scRNA donors, fall back to the 7 Visium polyp
  captures as an illustrative endpoint and say plainly that the spatial claim is
  descriptive.
- **Drop order if time runs short:** the OT correspondence analysis, then the
  genotype extension, then the CRC direction check, then the Visium illustration. The paired route analysis is the deliverable.

## Carcinoma subtype is not available

The epithelial objects carry no MSS/MSI-H label — every malignant specimen is one
`UNC` bucket, 7 donors. MSS (5 donors) and MSI-H (2 donors) appear only in the
non-epithelial object. **No "across cancer types" contrast is supported in the
scRNA data we can obtain.** The one well-powered MSS/MSI resource is the OSF
spatial atlas (97 exomes typed MSS 48 / MSI 37, joinable to the Visium captures),
but those are different donors and it is a carcinoma-versus-carcinoma question.

## What this design cannot claim

Somatic clonality, founder mutations, phylogeny, observed progression, or any
probability that a given polyp becomes cancer. Cell-state ordering is
cross-sectional and a trajectory is not observed ancestry. An optimal-transport
coupling between normal and polyp cells is a transcriptional correspondence, not
a lineage map, and gets no directional language. Seven CRC specimens do not make
a three-stage study, and 5 versus 2 donors do not make a cancer-subtype study.
