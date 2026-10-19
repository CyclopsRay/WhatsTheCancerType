# HTA11 — Weekly Report, week ending Friday 2026-10-23

Reporting interval: [2026-10-16T18:00:00+04:00, 2026-10-23T18:00:00+04:00) — Asia/Dubai.

Measured results only, with provenance; include positive and negative findings.

## 2026-10-19 — First paired analysis end to end: composition, DE, route split, replication, Visium

All numbers from tables under `/l/users/yuqi.lei/HTA11/derived/` (not in git; regenerate
with the scripts named). Figures in `figures/` via `scripts/make_figures.py`. Slurm jobs:
325071 (pseudobulk), 325099 (OSF download), 325107 (paired analysis), 325109 (Visium).
Methods: [10_23_record.md](10_23_record.md).

### Data inspection (`scripts/build_pseudobulk.py` → `derived/pseudobulk/`)

| Object | Cells | Genes | Specimens | Specimen×state groups |
|---|---|---|---|---|
| DIS epithelial | 65,088 | 33,703 | 62 | 505 |
| VAL epithelial | 57,723 | 30,104 | 59 | 475 |

`raw/X` holds integer counts; `X` is a dense normalized matrix. `Cell_Type` has nine
states: ABS, ASC, CT, EE, GOB, SSC, STM, TAC, TUF. Assay is TruDrop for every cell.
Median per-specimen mitochondrial fraction is high in DIS (37–44 %) and lower in VAL
(25–28 %). These objects are the authors' post-QC release, so no further cell
filter was applied; this is a QC item to revisit.

Paired donors per object (normal + that route): DIS conventional 11, serrated 9;
VAL conventional 8, serrated 6. These sum to the 19 / 15 quoted for the held data.

### Negative: OSF MxIF quantification tables are empty

All 16 `MxIF/quantification/*_threshold_quantification.csv` on OSF hftq2 are 0 bytes
(md5 `d41d8cd98f00b204e9800998ecf8427e`, created 2023-11-17). Full inventory of the
deposit (149 entries): `record/006_feasibility/osf_hftq2_inventory.tsv`. Every other
OSF folder has non-empty files (ST 50 files 12.1 GB, ST_master 48 / 5.6 GB, scRNA 9 / 4.0 GB,
VUMC_NMF 8 / 0.2 GB, WES 11 / 0.14 GB).

### Paired state composition (`derived/paired/composition_paired.tsv`)

Lesion-specific states, donor-level change in % of specimen epithelium (polyp − own normal):

| Object | Route | State | Donors | Median Δ (pp) | Donors up | Wilcoxon p | BH padj |
|---|---|---|---|---|---|---|---|
| DIS | conventional | ASC | 11 | +23.9 | 10 | 0.003 | 0.053 |
| DIS | serrated | SSC | 9 | +21.5 | 7 | 0.020 | 0.088 |
| VAL | conventional | ASC | 8 | +47.5 | 6 | 0.039 | 0.117 |
| VAL | serrated | SSC | 6 | +16.9 | 6 | 0.031 | 0.117 |

ABS (absorptive) falls in 9/11, 8/9, 7/8 and 3/6 donors respectively. Small serrated
increases in ASC also occur (DIS 8/9, VAL 6/6 donors up, median +3.3 / +1.2 pp).
BH is over 9 states × 2 routes per object. With 6 donors the smallest attainable
two-sided signed-rank p is 0.031, so donor counts carry more information than padj here.

Median share by polyp subtype (all specimens, not paired): SSC is 17.4 % (DIS) / 21.8 %
(VAL) in HP and 22.6 % / 16.0 % in SSL; ASC is 22.7 % / 31.8 % in TA and 50.0 % / 74.6 % in
TVA (n=2 each). HP and SSL are compositionally alike on this axis.

### Paired pseudobulk DESeq2, `~ donor + condition` (`derived/paired/de_summary.tsv`)

padj < 0.05 and |log2FC| > 1; specimens with ≥30 cells (per state: ≥30 cells of that state).

| Object | Route | Scope | Donors | Specimens | Genes tested | Up | Down |
|---|---|---|---|---|---|---|---|
| DIS | conventional | all epithelium | 11 | 27 | 18,865 | 507 | 220 |
| DIS | serrated | all epithelium | 9 | 23 | 17,943 | 483 | 163 |
| VAL | conventional | all epithelium | 8 | 22 | 17,397 | 786 | 621 |
| VAL | serrated | all epithelium | 6 | 17 | 16,806 | 504 | 153 |
| DIS | conventional | ABS | 11 | 27 | 13,499 | 83 | 40 |
| DIS | serrated | ABS | 9 | 23 | 15,134 | 149 | 90 |
| DIS | conventional | GOB | 8 | 20 | 13,473 | 385 | 231 |
| DIS | serrated | GOB | 6 | 15 | 12,282 | 100 | 33 |
| DIS | conventional | TAC | 7 | 18 | 12,413 | 407 | 324 |
| DIS | serrated | TAC | 6 | 15 | 10,815 | 99 | 39 |
| VAL | conventional | ABS | 7 | 20 | 13,002 | 373 | 318 |
| VAL | serrated | ABS | 6 | 17 | 13,688 | 91 | 30 |
| VAL | conventional | GOB | 5 | 14 | 11,506 | 345 | 190 |
| VAL | serrated | GOB | 6 | 17 | 9,157 | 125 | 46 |
| VAL | conventional | TAC | 6 | 17 | 9,834 | 65 | 17 |
| VAL | serrated | TAC | 6 | 15 | 10,592 | 9 | 0 |

### Shared vs route-specific (`derived/paired/route_compare_{DIS,VAL}_all.tsv`)

Route-specific = significant in one route only **and** route difference z-test BH < 0.05.

| Category | DIS | VAL |
|---|---|---|
| shared (both routes, same sign) | 224 | 244 |
| conventional-specific | 53 | 226 |
| serrated-specific | 68 | 76 |
| one route only, difference n.s. | 691 | 1,077 |
| opposite direction | 3 | 3 |

LFC correlation between routes (DIS, all genes): Spearman 0.37.
DIS examples: shared up MUC5AC, REG4, CLDN2, KLK10, S100P, DUOX2, TIMP1; shared down
HSD3B2, CLCA4, SLC51A, AQP8, ZG16, MEP1B; conventional-specific up APCDD1, NKD1, DPEP1,
ASCL2, MMP7; serrated-specific up TFF1, TFF2, SLC6A14, ANXA1, IRS1.

Do DIS route categories hold in VAL? Shared genes (208 testable): 100 % same sign in both
routes in VAL. Conventional-specific (48): 100 % same sign in conventional, 91.7 % larger
in conventional than serrated; strict VAL category match 43.8 %. Serrated-specific (65):
98.5 % same sign, 95.4 % larger in serrated; strict match 35.4 %.

### Replication DIS → VAL (`derived/paired/replication_summary.tsv`)

| Route | Scope | DIS hits tested in VAL | Same sign | Also padj<0.05 in VAL | Spearman LFC, all genes |
|---|---|---|---|---|---|
| conventional | all | 662 | 98.9 % | 486 | 0.69 |
| serrated | all | 615 | 97.4 % | 381 | 0.60 |
| conventional | ABS | 113 | 93.8 % | 67 | 0.50 |
| serrated | ABS | 223 | 92.4 % | 49 | 0.37 |
| conventional | GOB | 517 | 98.3 % | 292 | 0.66 |
| serrated | GOB | 102 | 98.0 % | 51 | 0.39 |
| conventional | TAC | 501 | 94.4 % | 67 | 0.56 |
| serrated | TAC | 105 | 94.3 % | 7 | 0.23 |

Donor consistency (`donor_consistency_DIS_*.tsv`): median DIS-significant gene agrees in
sign in 82 % of conventional donors (74 % of genes in ≥80 % of donors; 7 % in all 11)
and 89 % of serrated donors (67 % ≥80 %; 21 % in all 9).

### Hallmark GSEA (`derived/paired/gsea_*_all.tsv`, NES / FDR)

| Set | DIS conv | DIS serr | VAL conv | VAL serr |
|---|---|---|---|---|
| Wnt/β-catenin | +1.96 / 0.002 | −1.22 / 0.17 | +1.64 / 0.024 | −1.60 / 0.015 |
| TNF-α via NF-κB | +1.11 / 0.45 | +2.06 / <0.001 | −1.48 / 0.022 | +1.83 / 0.002 |
| Inflammatory response | +1.49 / 0.035 | +1.84 / 0.001 | −1.08 / 0.33 | +1.93 / 0.001 |
| Oxidative phosphorylation | −3.52 / <0.001 | −2.32 / <0.001 | −3.59 / <0.001 | −2.54 / <0.001 |

DIS FDR<0.05 sets: 25 conventional, 29 serrated.

### Visium polyp sections (`scripts/visium_scoring.py` → `derived/visium/`)

Signatures: top 50 DIS genes per category (shared up, conventional-specific up,
serrated-specific up, shared down), `scanpy.tl.score_genes` on log-normalized counts.
AUC = Mann–Whitney U / (n₁n₂), lesion (`adenoma`) vs `normal_mucosa` spots on the same section.
Spots are not independent; these are descriptive.

| Section | Type | Lesion / normal spots | conv-up AUC | serr-up AUC | shared-up AUC | shared-down AUC |
|---|---|---|---|---|---|---|
| 8270_1 (HTA11_07862) | TA/TVA | 377 / 388 | 0.64 | 0.55 | 0.58 | 0.35 |
| 8270_2 (HTA11_10711) | TA/TVA | 291 / 123 | 0.63 | 0.50 | 0.55 | 0.55 |
| 8270_3 (HTA11_07663) | SSL/HP | 539 / 253 | 0.46 | 0.62 | 0.59 | 0.37 |
| 8270_5 (HTA11_06134) | SSL/HP | 86 / 143 | 0.49 | 0.96 | 0.96 | 0.29 |

The other three polyp captures (7319_2, 7319_3, 7319_4) have no normal-mucosa spots.
HTA11_10711 is the only Visium polyp donor also in our scRNA (VAL, TA).

### Not used, recorded

OSF `scRNA/abnormal_epithelium.h5ad`: 8,153 cells × 16,464 genes, `X` float
(not raw counts), `Cell_Type` ASC 3,312 / CSC 3,706 / SSC 1,135, `Tumor_Type` MSS 2,434 /
MSI 272 / TA-TVA 454 / SSL-HP 389 cells (4,604 NA).
