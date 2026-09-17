# 004 — Roadmap scope and feasibility notes

Date: 2026-09-17. AI-assisted brainstorming and evidence notes only; neither
student should copy these into the assignment. Each writes and types their own
six answers. No completed submission question or hypothesis is supplied here.

## User clarification and proposed scope

The user clarified that “race types” meant disease/polyp subtypes, not patient
race or ethnicity. The following is a recommendation, pending team selection.

| Decision | Recommended working choice |
|---|---|
| Species and organ | Human large bowel: colon and rectum; retain exact anatomical site and check colon-only sensitivity where donor coverage permits |
| Cancer histology | Primary colorectal adenocarcinoma, with a documented MSS endpoint for the conventional-route analysis |
| Precancer | Conventional tubular adenoma (TA) and tubulovillous adenoma (TVA); pool for the main adenoma contrast while retaining subtype labels |
| Reference | Histologically normal/non-neoplastic colorectal mucosa; distinguish healthy-donor tissue from mucosa collected from patients with lesions |
| Separate route | Hyperplastic polyps and sessile serrated lesions; keep outside the primary contrast; MSI-H CRC is separate too |
| Cellular focus | Epithelial stem-like, proliferative and differentiated programs; immune/stromal cells provide targeted spatial context |

MSS is a measured molecular subtype, not proof of a particular tumor's precursor
or a substitute for unavailable DNA. Retain unknown MSI status as unknown. TA
and TVA are histological subtypes, not observed consecutive time points.

## Question-building decisions, not submission wording

The original idea is an open-ended research direction. A hypothesis additionally
requires an expected direction and an observation that could contradict it.
Replace the ambiguous causal quantity “contribute most” with explicit outcomes:

| Outcome | Measurement and analysis | Interpretation |
|---|---|---|
| Cell-state abundance | Fraction of captured epithelial cells in each state per specimen; donor-aware contrast and uncertainty | Relative representation in the sampled epithelial compartment |
| Within-state changes | Raw-count pseudobulk per specimen/state; donor-aware edgeR or limma-voom design; effect sizes, FDR and pathway enrichment | Expression changes distinct from changing cell composition |
| Spatial localization | Fixed RNA program scores in Visium with histology regions; region differences summarized per specimen | Regional distribution; Visium spots can contain several cell types |
| Optional immune relationship | MxIF CD8-cell density inside/around epithelial regions, or distances using existing cell coordinates | Spatial association, conditional on suitable markers and segmentation |

Hypothesis ingredients to consider: greater stem-like/WNT and proliferation
activity in neoplastic epithelium, altered differentiation, and broader spatial
distribution than the normal crypt-base compartment. These are prior-informed
expectations, not project findings; evaluate each contrast without forcing a
monotonic trend. A reproducible opposite direction, no detectable difference, or
strong donor dependence would change the interpretation. Candidate anchors to
check against fixed published gene sets include LGR5 (stem-like), MKI67
(proliferation) and KRT20 (differentiation). Single markers are not definitive
cell identities; stemness and proliferation must be assessed separately.

The added value for this course project is quantifying donor consistency and
spatial variation in established programs. Cross-sectional expression and images
support associations with pathology, not causal attribution or observed lineage.

## Evidence and access distinctions

- [Chen et al., Cell 2021](https://pmc.ncbi.nlm.nih.gov/articles/PMC8941949/)
  supplies the conventional-versus-serrated distinction and the reference RNA
  resource. Its CRC RNA arm reports seven fresh specimens (five MSS, two MSI-H).
  That is a publication-level count, not an audited count in our downloaded files.
- [Heiser et al., Cell 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10756562/)
  describes 31 spatial specimens: 12 MSS CRC, 10 MSI-H CRC, four TA/TVA, four
  SSL/HP, and one normal control. Visium, MxIF and H&E are relevant inputs.
  These are study-wide counts, not a verified downloadable analysis subset.
  One normal specimen supports a reference illustration, not a replicated
  normal-versus-disease spatial group test. Prioritize adenoma/CRC comparisons
  and within-specimen regional contrasts for spatial inference if accessible.
- The spatial authors provide [analysis code](https://github.com/Ken-Lau-Lab/spatial_CRC_atlas),
  [imaging code](https://github.com/Ken-Lau-Lab/spatial_CRC_atlas_imaging),
  and an [OSF processed-data source](https://osf.io/hftq2/), as well as HTAN.
  File access, coverage, region annotations and marker tables remain unaudited.
  Prefer processed spatial matrices and existing segmentation over rebuilding
  a whole-slide image pipeline within the course schedule.
- Public [CELLxGENE collection API](https://api.cellxgene.cziscience.com/curation/v1/collections/a48f5033-3438-4550-8574-cdff3263fdfd)
  was fetched again; the response is preserved as
  [cellxgene_collection.json](cellxgene_collection.json). The three downloaded
  assets are DIS epithelial, VAL epithelial and combined non-epithelial. The
  description mentions an “Abnormal” object containing CRCs, but the API exposes
  no separately titled Abnormal asset. DIS disease labels include the broad
  “colorectal neoplasm”; VAL includes “colorectal cancer.” These vocabulary
  labels do not establish histology, MSS status, or usable CRC replication.
- Earlier project inspection found overlapping donor identifiers between DIS
  and VAL. Therefore do not call the split donor-independent, or assume all
  three pathology groups occur in both. Inspect H5AD observations and published
  specimen mappings; separate shared donors before claiming independent validation.

Marker background: [Baker et al., characterization of LGR5 in colorectal
adenomas and carcinomas](https://pmc.ncbi.nlm.nih.gov/articles/PMC4345329/).
Candidate tool references: [Seurat spatial workflows](https://satijalab.org/seurat/articles/spatial_vignette),
[edgeR](https://bioconductor.org/packages/release/bioc/html/edgeR.html).

## Required early decisions for a ten-week scope

1. Audit actual RNA donor/specimen/pathology/MSI/site labels and count availability.
   Recover an explicitly mapped CRC matrix if the downloaded assets lack one.
2. In the same first week, audit spatial access, donor replication, region labels
   and marker coverage. Spatial evidence is required if spatial organization is
   part of the main question; it cannot be postponed as an optional Week 9 extra.
3. Freeze one main RNA contrast and one spatial endpoint. If spatial access fails,
   explicitly revise the question to RNA outcomes. If the three-stage RNA cohort
   fails, retain a supported normal/adenoma study and label a separate CRC endpoint
   analysis as such; do not confound study differences with disease differences.
4. Fix programs before replication; audit donors shared between RNA/spatial
   studies too. Matched modalities corroborate localization, but do not provide
   independent-patient validation.
5. Prioritize RNA plus one usable spatial assay. Additional cohorts, a second
   spatial assay, trajectory analysis and ML are extensions, not prerequisites.

No expression matrices were loaded, no new jobs were submitted, and no
biological results were generated in this review. The operational schedule is
in [PLAN.md](../../PLAN.md); the personal writing prompts are in
[ROADMAP_WORKSHEET.md](../../ROADMAP_WORKSHEET.md).
