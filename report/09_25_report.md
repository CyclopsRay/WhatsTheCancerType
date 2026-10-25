# HTA11 — Weekly Report, week ending Friday 2026-09-25

Reporting interval: [2026-09-18T18:00:00+04:00, 2026-09-25T18:00:00+04:00) — Asia/Dubai.

Measured results only, with provenance; include positive and negative findings.

## 2026-09-18 — HTA11 open-access inventory and cohort composition

Source: HTAN portal release manifest `processed_syn_data.json`, fetched
2026-09-18 16:27 UTC (`etag c8f67f6d4a0023ec76fc3ffa8b5bee93`), 221,253 files
across 14 atlases; 3,340 rows are HTA11. Derived tables and method in
[record 005](../record/005_open_access_audit/README.md). No expression matrix was
loaded; these are metadata counts.

### Obtainable without a dbGaP request

| Assay | Level | Source | Files | Biospecimens | Participants |
|---|---|---|---|---|---|
| scRNA-seq | 3 | Synapse | 364 | 245 | 130 |
| scRNA-seq | 4 (H5AD) | Synapse | 6 | 210 | 106 |
| 10X Visium | 3 | Synapse | 170 | 32 | 31 |
| 10X Visium | 4 (H5AD) | Synapse | 43 | 32 | 31 |
| 10X Visium | Auxiliary (TIF) | Synapse | 47 | 32 | 31 |
| MxIF | 2 | CRDC-GC/SB-CGC open | 240 | 46 | 45 |
| H&E | 2 | CRDC-GC/SB-CGC open | 50 | 50 | 50 |
| CODEX | 2 | CRDC-GC/SB-CGC open | 20 | 20 | 20 |
| NanoString GeoMx DSP | 2 | Synapse | 20 | 20 | 20 |
| Bulk DNA (WES) | 3 (VCF) | Synapse | 253 | 174 | 153 |

Behind dbGaP (special request): scRNA L1 540 / L2 281; Visium L1 90 / L2 43;
Bulk DNA L1 782 / L2 391. Every file the project needs is outside that tier.

**Correction to a previously recorded fact.** `KNOWLEDGE.md` recorded on
2026-09-17 that Vanderbilt provides no usable DNA result files including Level 3.
The release manifest lists 253 open Bulk DNA **Level 3 VCFs** on Synapse over 153
participants, 85 of which are also scRNA Level-4 participants. Usability of the
calls is a separate, still-unverified question (item 1 below).

### scRNA Level-4 cohort composition and donor pairing

| Group | Specimens | Donors |
|---|---|---|
| Normal | 90 | 59 |
| Tubular adenoma (M82110) | 59 | 49 |
| Tubulovillous adenoma (M82630) | 7 | 7 |
| Serrated adenoma / SSL (M82130) | 23 | 21 |
| Hyperplastic / atypia | 17 | 17 |
| CRC primary | 7 | 7 |
| NOS / other | 7 | 6 |

Within-donor pairs: normal + conventional **28 donors**; normal + serrated
**21 donors**; normal + primary CRC **3 donors**; conventional + serrated
3 donors. Level 3 gives the same pairing with 18 rather than 7 CRC donors.

Negative result for the three-stage design: the polyp-to-carcinoma arm is
n=7 specimens with no within-donor pairing, so a normal/adenoma/CRC progression
claim is not supported at the power the normal/polyp arm has.

### Spatial coverage

Visium Level 4: 43 captures / 31 participants, of which **7 captures are polyps**
(`8270_AS_1`, `8270_AS_2` TA; `7319_AS_4` TVA; `7319_AS_2`, `7319_AS_3`,
`8270_AS_3` SSL; `8270_AS_5` HP). Remainder are primary CRC, metastases, or
unlabelled. Visium shares only 10 participants with scRNA Level 4.

MxIF Level 2: 46 biospecimens / 45 participants — 13 TA, 2 TVA, 7 SSL,
6 HP/atypia, 3 normal, 7 primary CRC — and shares **32** participants with
scRNA Level 4. Released only as images; no segmented cell table on the portal.

### Anonymous mirror at OSF `hftq2`

No account required. `ST/` 50 per-capture Visium H5ADs; `ST_master/` 48 annotated
H5ADs; `MxIF/quantification/` 16 per-specimen segmented threshold cell tables;
`scRNA/` including `abnormal_epithelium.h5ad` and `VUMC_NMF/` with the published
k=30 gene spectra; `WES/` maftools-ready somatic calls. `master_depth15_
clinicalData.txt` (downloaded, 97 flagged samples) types the spatial exome cohort
MSS 48 / MSI 37 / TA-TVA 8 / SSL-HP 4 — the spatial cohort's exomes, distinct
from the 253 polyp VCFs on Synapse.

The MxIF quantification tables remove whole-slide segmentation from the critical
path; this is the finding that makes an MxIF spatial arm affordable in ten weeks.

### Three Level-4 H5ADs not in the CELLxGENE collection

`VUMC_ABNORMALS_EPI_V2.h5ad` (syn27056096), `VUMC_HTAN_NEWCo_EPI_V2.h5ad`
(syn51069188), `VUMC_HTAN_All_NonEPI_V2.h5ad` (syn51069186). This resolves the
open question about the missing "Abnormal" object recorded on 2026-09-17: it is
released on Synapse, not through CELLxGENE.

### Unverified

1. The 253 VCFs are named `MAP.*_polyp.rmdup.indel.recal-filtered.vcf` — GATK
   germline-style, no matched-normal token. Somatic usability unchecked.
2. Synapse download from this host has not been exercised; `downloadSource` in
   the manifest is the only access evidence.
3. HTAN biospecimen IDs have not been matched to `obs` columns inside the
   downloaded H5ADs. All counts above are portal metadata, not matrix contents.
4. 161 HTA11 biospecimens are `Not Otherwise Specified`, including 13 Visium
   captures; these are unresolved, not confirmed normals.

## 2026-09-18 (later) — First read of H5AD `obs`: the Week-1 cohort gate

Read with `h5py` from `/nfs-stor/yuqi.lei/envs/promotervi`, metadata groups only,
no expression matrix loaded. This replaces portal metadata with matrix contents
for the three objects we hold.

### Gate passed: the join works

All three objects carry `HTAN Specimen ID` and `donor_id` in `obs`, so HTAN
biospecimen IDs map onto cells directly. The paired within-donor design is
constructible. Also present: `Sample_Classification`, `Polyp_Type` (epithelial)
or `Tumor_Type` (non-epithelial), `disease`, `tissue`, `Cell_Type`, `sex`,
`self_reported_ethnicity`.

### What we actually hold, versus the full release

| | Specimens | Donors |
|---|---|---|
| Full Level-4 release (6 objects, portal metadata) | 210 | 106 |
| **Downloaded (DIS + VAL epithelial)** | **121** | **55** |

DIS 62 specimens / 30 donors, VAL 59 / 26, **donor overlap = 1**, specimen
overlap = 0. Non-epithelial object: 116 specimens / 59 donors.

Paired within-donor counts **in the data we hold**:

| Pair | Donors |
|---|---|
| Normal + conventional adenoma (AD) | **19** |
| Normal + serrated (SER) | **15** |
| Normal + CRC (UNC) | 5 |
| Conventional + serrated in the same donor | 1 |

Group totals held: NL 43 donors / 66 specimens; AD 26 / 29; SER 18 / 19;
UNC 7 / 7. By `Polyp_Type`: TA 24 donors, SSL 8, HP 10, TVA 2 (+ TV 2).

**Correction.** `ROADMAP.md`, `ROADMAP_CONCISE.md` and `PLAN.md` quote 28 and 21
paired donors. Those are the full-release numbers. The correct figures for the
downloadable subset are **19 and 15**. The larger numbers require the three
Synapse-only Level-4 objects, which the user reports are currently blocked by a
governance issue.

**Correction.** `KNOWLEDGE.md` recorded that DIS and VAL donor lists overlap and
that independent-donor validation needed auditing. Measured overlap is **one
donor**. DIS and VAL are effectively donor-disjoint and usable as discovery and
validation.

### Cancer-type annotation: present, but thin and in the wrong object

Epithelial objects carry **no carcinoma subtype**. All malignant specimens fall
into a single `Sample_Classification == "UNC"` bucket — 2 specimens in DIS
(`disease == "colorectal neoplasm"`), 5 in VAL (`disease == "colorectal
cancer"`), 7 donors total, 5,514 cells.

MSS and MSI-H appear **only in the non-epithelial object**, as
`Sample_Classification` and `Tumor_Type` values:

| Label | Specimens | Donors | Cells |
|---|---|---|---|
| MSS | 5 | 5 | 1,261 |
| MSI-H | 2 | 2 | 1,048 |

So a carcinoma-subtype contrast is n=5 versus n=2 donors, in immune and stromal
cells only. Subtyped malignant *epithelium* is presumably in
`VUMC_ABNORMALS_EPI_V2.h5ad` (syn27056096), which we do not hold.

The only well-powered MSS/MSI material found so far is the spatial atlas on OSF:
`WES/master_depth15_clinicalData.txt` types 97 samples MSS 48 / MSI 37, and 12 of
the 48 `ST_master/` Visium captures match those barcodes by filename alone
(MSS 9, MSI 2, TA/TVA 1); the rest presumably carry the label inside `obs`.
That is a carcinoma-versus-carcinoma comparison in spatial data, on different
donors from the scRNA cohort.

### Two further metadata facts

`tissue` resolves seven anatomical sites (ascending, transverse, descending,
sigmoid, hepatic cecum, hepatic flexure, rectum). But **every donor has exactly
one site label** — zero donors are sampled at more than one site. Site is
therefore a donor-level variable, fully confounded with donor, and the matched
normal is site-matched to its polyp by construction. Site can be tested between
donors only.

`Polyp_Type` vocabulary is inconsistent across objects: DIS writes `TVA`, VAL
writes `TV` for tubulovillous adenoma. Harmonize before pooling.
