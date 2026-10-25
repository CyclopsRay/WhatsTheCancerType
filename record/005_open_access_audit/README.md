# 005 — What HTA11 data is obtainable without a special access request

Date: 2026-09-18. Machine audit of the HTAN portal's own file inventory plus the
authors' OSF deposit. This supersedes the file counts quoted in `KNOWLEDGE.md`
from the user's manual portal browse on 2026-09-17, and **corrects the durable
claim that DNA results are unavailable.**

## Method

`https://humantumoratlas.org/processed_syn_data.json` (388 MB, fetched
2026-09-18 16:27 UTC, `etag c8f67f6d4a0023ec76fc3ffa8b5bee93`) is the portal's
released manifest: 221,253 files across 14 atlases, plus biospecimen, diagnosis,
demographics and therapy tables. 3,340 rows carry `atlasid == HTA11`
("HTAN Vanderbilt", Colon Molecular Atlas Project; portal header now reports
192 cases / 429 biospecimens). Each row exposes `level`, `downloadSource`,
`isRawSequencing`, `biospecimenIds` and `viewers`, so access tier is read from
the release rather than inferred. A local copy is kept at
`/nfs-stor/yuqi.lei/HTA11/data/htan_portal/processed_syn_data.json`.

HTA11 diagnosis records are almost entirely `Not Reported`. **Pathology for this
atlas lives on the biospecimen record**, in `TumorTissueType` plus the ICD-O-3
`HistologicMorphologyCode`: `M82110` tubular adenoma, `M82630` tubulovillous
adenoma, `M82130` serrated adenoma/SSL. The grouping used in the derived tables
is written out in `hta11_specimen_pathology.tsv` and can be recomputed.

## Access tiers

| Tier | What it takes | HTA11 content |
|---|---|---|
| Anonymous | nothing | OSF deposit `osf.io/hftq2`; MxIF Minerva viewers; CELLxGENE H5ADs |
| Free account, no review | Synapse account + accept HTAN terms; or CRDC-GC/SB-CGC open-access account | all Level 3/4 matrices, **Bulk DNA Level 3 VCFs**, MxIF/H&E/CODEX/GeoMx Level 2 images |
| **Special request** | dbGaP Data Access Request through an institutional signing official | every Level 1/2 sequencing file (FASTQ/BAM) — scRNA, Visium, Bulk DNA |

Only raw sequencing sits behind a request. Nothing this project needs does.

## Result — `hta11_access_summary.tsv`

Obtainable without a special request (files / biospecimens / participants):

| Assay | Level | Source | Files | Biospec | Participants |
|---|---|---|---|---|---|
| scRNA-seq | 3 (count matrices) | Synapse | 364 | 245 | 130 |
| scRNA-seq | 4 (annotated H5AD) | Synapse | 6 | 210 | 106 |
| 10X Visium | 3 (mtx + positions) | Synapse | 170 | 32 | 31 |
| 10X Visium | 4 (H5AD) | Synapse | 43 | 32 | 31 |
| 10X Visium | Auxiliary (slide TIFs) | Synapse | 47 | 32 | 31 |
| MxIF | 2 (TIF / OME-TIFF) | CRDC-GC/SB-CGC open | 240 | 46 | 45 |
| H&E | 2 | CRDC-GC/SB-CGC open | 50 | 50 | 50 |
| CODEX | 2 (OME-TIFF) | CRDC-GC/SB-CGC open | 20 | 20 | 20 |
| NanoString GeoMx DSP | 2 (OME-TIFF) | Synapse | 20 | 20 | 20 |
| **Bulk DNA (WES)** | **3 (VCF)** | **Synapse** | **253** | **174** | **153** |

Behind dbGaP: scRNA Level 1 (540) / Level 2 BAM (281); Visium Level 1 (90) /
Level 2 BAM (43); Bulk DNA Level 1 (782) / Level 2 (391).

### The six Level-4 scRNA objects

`VUMC_Discovery_Epithelial.h5ad` (syn53710088), `VUMC_Validation_Epithelial.h5ad`
(syn53710094), `VUMC_val_dis_Non_Epithelial.h5ad` (syn53710089) — these three are
the CELLxGENE assets already downloaded. Also released, and **not** exposed by
the CELLxGENE API: `VUMC_ABNORMALS_EPI_V2.h5ad` (syn27056096, 55 biospecimens),
`VUMC_HTAN_NEWCo_EPI_V2.h5ad` (syn51069188, 79), `VUMC_HTAN_All_NonEPI_V2.h5ad`
(syn51069186, 195). This resolves the open question about the missing "Abnormal"
object: it exists on Synapse, not in the CELLxGENE collection. Each also has an
ISB-CGC BigQuery mirror (`isb-cgc-bq.HTAN.scRNAseq_VUMC_*`).

## Cohort composition of the open scRNA release — the decisive number

Biospecimens (donors) in the Level-4 release, by pathology group:

| Group | Specimens | Donors |
|---|---|---|
| Normal | 90 | 59 |
| Tubular adenoma | 59 | 49 |
| Tubulovillous adenoma | 7 | 7 |
| Serrated adenoma / SSL | 23 | 21 |
| Hyperplastic / atypia | 17 | 17 |
| CRC primary | 7 | 7 |
| NOS / other | 7 | 6 |

Within-donor pairing (`paired_donor_design.tsv`):

- **28 donors have both normal mucosa and a conventional (TA/TVA) polyp**
- **21 donors have both normal mucosa and a serrated (SSL/HP) lesion**
- only 3 donors have normal and primary CRC; only 3 donors span both routes

**Normal-to-polyp is a paired, donor-replicated design. Polyp-to-carcinoma is
not** — seven CRC specimens in Level 4 (18 donors at Level 3) with essentially no
within-donor pairing. Any three-stage claim would rest on between-donor CRC
comparison at n=7.

## Spatial coverage is CRC-weighted

Visium Level 4 is 43 captures over 31 participants, but only **7 captures are
polyps**: `8270_AS_1` (TA), `8270_AS_2` (TA), `7319_AS_4` (TVA), `7319_AS_2`,
`7319_AS_3`, `8270_AS_3` (SSL), `8270_AS_5` (HP). The rest are primary CRC,
metastases, and unlabelled ("Not Otherwise Specified") captures. Only 10 Visium
participants overlap the scRNA Level-4 donors.

MxIF is the better-matched spatial assay for a polyp question: 46 biospecimens /
45 participants — 13 TA, 2 TVA, 7 SSL, 6 HP/atypia, 3 normal, 7 primary CRC —
and **32 of its participants also appear in scRNA Level 4** (versus 10 for
Visium). Its cost is that HTAN releases MxIF only at Level 2 (images); there is
no released segmented cell table on the portal.

Participant overlap across open modalities (`hta11_access_summary.tsv` inputs):

|  | scRNA L4 | Visium | MxIF | H&E | WES VCF |
|---|---|---|---|---|---|
| scRNA L4 (106) | — | 10 | 32 | 28 | 85 |
| Visium (31) | 10 | — | 16 | 2 | 28 |
| MxIF (45) | 32 | 16 | — | 30 | 33 |
| WES VCF (153) | 85 | 28 | 33 | 38 | — |

## The authors' OSF deposit — anonymous, and it closes the MxIF gap

`https://osf.io/hftq2/` (Heiser et al. 2023 spatial CRC atlas) needs no account:

- `ST/` — 50 per-capture Visium H5ADs, `*_filtered_trimmed.h5ad`
- `ST_master/` — 48 per-capture H5ADs carrying the published annotations
- `MxIF/quantification/` — **16 per-specimen `*_threshold_quantification.csv`
  cell tables**, i.e. already-segmented, already-thresholded MxIF marker calls.
  This removes whole-slide segmentation from the critical path.
- `scRNA/` — `abnormal_epithelium.h5ad`, `VUMC_HTAN_DIS_EPI_V2.h5ad`,
  `VUMC_COMBINED.h5ad`, Broad comparison objects, `outer_combined_all4_dat.h5ad`,
  and `VUMC_NMF/` with the published k=30 NMF gene spectra
  (`VUMC_NMF.gene_spectra_score.k_30.dt_0_1.txt`) and embedding H5AD
- `WES/` — maftools-ready somatic calls: `master_depth15_maftools.maf`,
  `LCM_depth15_maftools.maf`, `pseudobulk_depth15_maftools.maf` with clinical
  tables. `master_depth15_clinicalData.txt` has 97 flagged samples typed
  MSS 48 / MSI 37 / TA-TVA 8 / SSL-HP 4 — this is the **spatial** cohort's
  exome set, distinct from the 253 polyp VCFs on Synapse.

Fetched `master_depth15_clinicalData.txt` and `master_depth15_geneSummary.txt`
to `/tmp` for the column check above; nothing else was downloaded.

## What is still unverified

1. The 253 Synapse VCFs are named `MAP.*_polyp.rmdup.indel.recal-filtered.vcf`.
   That naming is GATK germline-style with no matched-normal token. Whether they
   carry usable somatic calls, and whether `APC`/`KRAS`/`BRAF` status can be read
   per polyp, is unchecked. Do not build a required analysis arm on them before
   opening a few.
2. Whether a Synapse account plus HTAN terms is sufficient for these specific
   Level 3/4 entities has not been exercised from this host — the portal's
   `downloadSource` field is the only evidence so far.
3. The mapping from HTAN biospecimen IDs to the `obs` columns inside the
   downloaded H5ADs is unverified; the donor/pathology counts above come from the
   portal metadata, not from the matrices.
4. `TumorTissueType == "Not Otherwise Specified"` covers 161 HTA11 biospecimens,
   including 13 Visium captures. These are unresolved, not confirmed normals.

## Files here

- `hta11_access_summary.tsv` — assay x level x source, with per-group specimen counts
- `hta11_specimen_pathology.tsv` — one row per biospecimen in any open modality
- `paired_donor_design.tsv` — donor pairing counts for the scRNA release
