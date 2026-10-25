# HTA11 — Weekly Report, week ending Friday 2026-10-23

Reporting interval: [2026-10-16T18:00:00+04:00, 2026-10-23T18:00:00+04:00) — Asia/Dubai.

Measured results only, with provenance; include positive and negative findings.

## 2026-10-19 — First paired analysis end to end: composition, DE, route split, replication, Visium

All numbers from tables under `/nfs-stor/yuqi.lei/HTA11/derived/` (not in git; regenerate
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

## 2026-10-20 — Hypothesis checks X1–X6: does the route live in the departure from the donor's own normal?

Scripts `scripts/hypothesis_checks.py` (job 327343) and `scripts/pairing_benefit.py`
(job 327354); outputs `/nfs-stor/yuqi.lei/HTA11/derived/hypothesis/`. Pseudobulk only;
specimens or specimen×state groups with ≥30 cells; similarity = Pearson r on log-CPM
of the 2,000 most variable genes. Reasoning in [10_23_record.md](10_23_record.md).

### Two-route donor HTA11_6801 (VAL, sigmoid colon; `derived/pseudobulk/VAL_composition.tsv`)

| Specimen | Type | Cells | ASC % | SSC % |
|---|---|---|---|---|
| 2000002011 | normal | 495 | 0.0 | 0.0 |
| 2000002021 | normal | 1,194 | 0.0 | 0.1 |
| 2000001021 | TA | 1,014 | 6.4 | 1.6 |
| 2000001011 | SSL | 1,264 | 1.2 | 27.1 |

DIS-signature scores (`x3_HTA11_6801.tsv`, mean z): conventional-up TA +0.49, SSL −0.60,
normals −0.78 / −0.50; serrated-up TA +1.05, SSL +1.06, normals +0.06 / −0.38. The TA
carries the serrated program as strongly as the SSL; only the conventional program separates them.

Other multi-polyp donors (VAL): HTA11_6818 TA 59 % / TVA 84 % ASC; HTA11_8622 two SSL 66 % / 58 % SSC;
HTA11_11156 two TA 32 % / 16 % ASC (no normal). Unique donors with normal + a polyp, DIS ∪ VAL: 33.

### X1 — polyp closest to its own donor's normal (`x1_baseline_summary.tsv`)

| Scope | Polyps | Own normal ranks #1 | Expected by chance | Own normal in top 3 |
|---|---|---|---|---|
| all epithelium | 36 | 21 | 1.7 | 30 |
| ABS only | 35 | 22 | 1.7 | 26 |
| GOB only | 27 | 13 | 1.4 | 18 |

Candidate donors per polyp: median 24 (DIS) / 18–19 (VAL). Polyp and own normal share
processing, so batch cannot be separated from donor here.

### X2 — route separation, polyp alone vs polyp minus own normal (`x2_delta_summary.tsv`) — negative

| Object | Profile | Mean r within route | Mean r between routes | LOO nearest-centroid correct |
|---|---|---|---|---|
| DIS | polyp alone | 0.072 | −0.165 | 17 / 20 |
| DIS | minus own normal | 0.026 | −0.122 | 15 / 20 |
| VAL | polyp alone | 0.032 | −0.168 | 11 / 14 |
| VAL | minus own normal | 0.028 | −0.156 | 11 / 14 |

Subtracting the donor's normal does not improve coarse route separation in HVG space.

### X3 — DIS route signatures on VAL polyps (`x3_val_route_calls.tsv`)

Score = mean z of top-50 DIS conventional-specific-up minus serrated-specific-up genes.
Raw call (threshold = median of VAL normals): 20 / 23 polyps correct; 13 / 16 among polyps
with an own normal. Delta call (minus own normal, threshold 0): 14 / 16. Errors: HTA11_7862 TA
(ASC 0 %), HTA11_6801 TA (both calls), HTA11_7469 TA (raw only).

### X4 — which normal state of the same donor each lesion state resembles (`x4_resemblance.tsv`)

| Lesion state | Donors | Closest normal state | Median r to: STM / TAC / ABS / GOB |
|---|---|---|---|
| ASC (conventional polyps) | 13 | STM 10, ABS 2, TAC 1 | 0.59 / 0.53 / 0.53 / 0.52 |
| SSC (serrated polyps) | 10 | ABS 10 | 0.37 / 0.32 / 0.62 / 0.52 |

Second-closest: ASC → TAC 5, GOB 4, ABS 3, STM 1; SSC → GOB 9, CT 1.

### X5 — route bias inside a fixed state (`x5_withinstate.tsv`)

All-epithelium route-specific genes that keep the larger effect in their own route when
refit inside one state: 86.6–100 % across 12 object × state × category cells (DIS n = 21–59
genes, VAL n = 24–214). Formally route-specific again inside the state: 0–28.6 %.

### X6 — paired vs unpaired DESeq2 on identical specimens (`x6_pairing_summary.tsv`)

| Route | Model | DIS hits | VAL hits | DIS hits same sign in VAL | Also padj<0.05 in VAL | Median DIS lfcSE |
|---|---|---|---|---|---|---|
| conventional | ~donor + condition | 727 | 1,407 | 98.9 % (662) | 73.4 % | 0.20 |
| conventional | ~condition | 585 | 1,617 | 98.5 % (533) | 74.1 % | 0.24 |
| serrated | ~donor + condition | 646 | 657 | 97.4 % (615) | 62.0 % | 0.21 |
| serrated | ~condition | 607 | 601 | 97.7 % (571) | 59.7 % | 0.25 |

Pairing gives more hits in 3 of 4 fits and ~16 % smaller standard errors; replication rates are
unchanged. Paired hit counts reproduce the 10-19 run (507 + 220 = 727).

### Deck

Midterm deck rebuilt to 11 slides (story order), same URL; sources in
`presentation/midterm_deck/project/`. New figure `figures/fig8_new_cells.png`.

## 2026-10-20 — Step 4 first run: same-person cell matching (unbalanced OT); marker check

`scripts/cell_matching.py` (test job 327373, full job 327374) →
`/nfs-stor/yuqi.lei/HTA11/derived/cell_matching/cm_{mapping,matched,cross}.tsv`.
Per object: 2,000 HVGs (MT-/RPL/RPS excluded) on a 30k-cell subsample, z-scored, 30 PCs
(variance 23 % DIS, 21 % VAL). Per donor × route: up to 2,000 polyp cells (source) vs up to
2,000 of the same donor's normal cells (target); log-domain unbalanced Sinkhorn, cost =
squared distance / median random-pair distance (320 DIS, 312 VAL). Main eps 0.05, rho 1;
grid eps {0.02, 0.1} × rho {0.3, 3}. 33 donor-route pairs (DIS 20, VAL 13; HTA11_6182
conventional skipped: 50 normal cells < 100). Enrichment = mass share to a normal state /
that state's share of the donor's normal cells; best healthy match = highest enrichment
among normal states with ≥20 cells, excluding the rare normal-labelled ASC/SSC cells.

### Positive control: polyp state → same normal state (main setting, median over donor-routes)

| Polyp state | ABS | GOB | TAC | CT | EE | TUF | STM |
|---|---|---|---|---|---|---|---|
| Median mass to same normal state | 0.90 | 0.90 | 0.81 | 0.83 | 0.94 | 0.91 | 0.28 |
| Donor-routes | 33 | 26 | 27 | 9 | 3 | 5 | 12 |

Polyp STM by raw mass mostly lands on normal ABS; by enrichment polyp STM → normal STM in 10 / 12.

### Lesion states: best healthy match per donor (all five settings)

| Lesion state | Donors | eps .05 / rho 1 | eps .02 / .3 | eps .02 / 3 | eps .1 / .3 | eps .1 / 3 |
|---|---|---|---|---|---|---|
| ASC (conventional) | 14 | STM 11, ABS 2, TAC 1 | STM 11, ABS 2, GOB 1 | STM 11, GOB 2, ABS 1 | STM 11, ABS 2, TAC 1 | STM 11, ABS 2, TAC 1 |
| SSC (serrated) | 10 | ABS 9, STM 1 | ABS 9, STM 1 | ABS 9, STM 1 | ABS 8, STM 2 | ABS 9, STM 1 |

Median enrichment (main): ASC → STM 2.75, normal-ASC 3.49, TAC 1.04, ABS 1.02; SSC → ABS 1.30,
STM 0.63, GOB 0.51. If the rare normal-labelled ASC cells are allowed as targets, ASC's top
target is STM 7 / ASC 6 / ABS 1. By raw mass share (not abundance-corrected) both lesion states
land mostly on ABS (median 0.51 ASC, 0.81 SSC), because ABS dominates normal tissue.
Also seen: serrated-polyp ASC cells → STM 5 / ASC 3 / TAC 1 of 9.

HTA11_6801 (both routes): its TA's ASC (65 cells) → STM enrichment 9.4, TAC 3.2, ABS 0.53;
its SSL's SSC (342 cells) → ABS 1.36, STM 0.63.

### Matched mass (transported / input, main setting, median over donors)

| Polyp state | ABS | ASC | SSC | STM | TAC | GOB | CT | EE | TUF |
|---|---|---|---|---|---|---|---|---|---|
| conventional | 0.87 | 0.61 | — | 0.85 | 0.72 | 0.64 | 0.73 | 0.59 | 0.48 |
| serrated | 0.88 | 0.77 | 0.60 | 0.82 | 0.85 | 0.75 | 0.86 | 0.36 | 0.71 |

Lesion state (ASC in conventional, SSC in serrated) less matched than the median of the
donor's other polyp states: 23 / 24 donor-routes. Rare states (EE, TUF) are also poorly matched.

### Own normal vs other donors' normal (800 cells per side, main setting)

Own normal has the lowest transport cost per unit mass in 10 / 33 donor-routes (chance ≈ 1.6);
median rank 3 of 24 candidates. Weaker than the pseudobulk fingerprint (X1, 21 / 36).

### Marker check of `Cell_Type` (`scripts/marker_check.py` → `derived/hypothesis/markers_*.tsv`)

Mean log-CPM per state over specimen × state groups with ≥30 cells, z-scored across states.
Markers peaking in their own label: TAC 3/3, GOB 4/4, EE 3/3, TUF 3/3, CT (BEST4, OTOP2, CA7)
3/3, SSC (MUC5AC, TFF1, ANXA10, AQP5) 4/4, ABS 3/4 (CEACAM7 peaks in CT) in both objects.
STM markers (LGR5, OLFM4, SMOC2, ASCL2) peak in **ASC**, with STM second (DIS z: LGR5 1.70 ASC /
1.05 STM); STM 0/4 DIS, 1/4 VAL. ASC: LGR5, ASCL2 peak in ASC; MYC peaks in STM; SOX9 in TUF.

## 2026-10-22 — Tissue pictures of one polyp per route (slide 2)

| Figure | Capture | Pathology | Polyp spots | Source |
|---|---|---|---|---|
| `figures/fig9_he_conventional.png` | 8270_1 (HTA11_07862), left tissue piece | TA/TVA, sigmoid | 406 (`adenoma` + `adenoma_border`) | OSF `ST_master/8270_1_HTA11_07862_master.h5ad`, hires H&E |
| `figures/fig9_he_serrated.png` | 8270_5 (HTA11_06134), whole strip | SSL/HP, sigmoid | 86 | OSF `ST_master/8270_5_HTA11_06134_master.h5ad`, hires H&E |

`python scripts/make_he_panels.py /nfs-stor/$USER/HTA11/data/osf_hftq2/ST_master figures`
(seconds, login node). Descriptive only: the conventional section is a thick crowded mass of
glands; the serrated section is a thin flat strip with normal mucosa between two polyp areas,
saw-tooth lumens visible in the upper polyp area. Rotated 90° clockwise for the slide.

## 2026-10-22 — Label-free map of the epithelium (job 332524)

`sbatch scripts/label_free_view.sh` → `derived/label_free/`, `figures/fig10_label_free_*.png`.
Our own embedding from `raw/X`: depth-normalise + log1p, 2,000 HVG (MT-/RPL/RPS out), scale,
30 PCs, UMAP (k=15). No batch/donor correction, no labels; normal + conventional + serrated cells.
Per cell, 30 nearest neighbours in PC space: share from healthy specimens, share from same person.

| Object | Cells | People | PC1 / PC2 variance | Same-person neighbours, median (normal / polyp) | Chance |
|---|---|---|---|---|---|
| DIS | 63,480 | 29 | 4.1 % / 3.2 % | 0.33 / 0.73 | 0.057 |
| VAL | 53,817 | 25 | 4.0 % / 3.0 % | 0.40 / 0.67 | 0.063 |

Polyp cells with ≤ 5 % healthy neighbours ("no healthy look-alike"; `no_healthy_neighbour_summary.tsv`):

| Object | Route | Polyp cells | No look-alike | Of those, labelled ASC/SSC | ASC/SSC share of polyp | ASC/SSC captured |
|---|---|---|---|---|---|---|
| DIS | conventional | 21,297 | 56.7 % | 47.5 % (ASC) | 30.4 % | 88.5 % |
| DIS | serrated | 11,843 | 50.7 % | 50.6 % (SSC) | 26.6 % | 96.4 % |
| VAL | conventional | 11,138 | 50.2 % | 65.8 % (ASC) | 36.3 % | 91.0 % |
| VAL | serrated | 8,671 | 42.6 % | 63.8 % (SSC) | 27.9 % | 97.4 % |

Healthy cells with ≤ 5 % healthy neighbours: 26 / 30,340 (DIS), 4 / 34,008 (VAL).
Spread over people: people with ≥ 20 % of their polyp cells lacking a look-alike — conventional
11 / 14 (DIS), 9 / 13 (VAL); serrated 8 / 11 (DIS), 4 / 7 (VAL). The largest single person holds
22 % / 45 % (conventional DIS / VAL) and 58 % / 52 % (serrated) of such cells.

One person, HTA11_6801 (VAL; map built from its 3,967 cells only; `person_6801_embedding.tsv.gz`):
the conventional polyp (1,014 cells), serrated polyp (1,264) and two healthy samples (1,689) occupy
largely separate regions; polyp absorptive cells do not overlap healthy absorptive cells.

Negative / caveats: PC1–PC2 carry 7 % of variance and mostly separate secretory (GOB/EE/TUF) from
absorptive cells, not routes; the PCA plot is not a route picture. Without correction, polyp cells
neighbour their own person's cells far more than healthy cells do (0.67–0.73 vs 0.33–0.40), so part
of the "no look-alike" share is person- or polyp-specific, and the serrated islands lean on one person.

### Stem vs mature-absorptive genes per person (job 332647; `derived/label_free/*_crypt_scores.tsv.gz`)

Per cell: mean log2(CPM+1) of stem markers (LGR5, OLFM4, SMOC2, ASCL2) and mature-absorptive
markers (CA1, SLC26A3, AQP8, CEACAM7), the `marker_check.py` sets. Then mean per person × tissue ×
`Cell_Type` (≥ 20 cells). Median over people [IQR]:

| Group | People | Stem | Mature |
|---|---|---|---|
| healthy STM | 31 | 2.30 [1.50–2.72] | 1.35 [0.93–1.54] |
| healthy ABS | 43 | 0.29 [0.20–0.54] | 5.24 [4.63–6.50] |
| ASC in conventional polyps | 22 | 3.17 [2.85–4.10] | 0.91 [0.47–1.33] |
| SSC in serrated polyps | 12 | 0.60 [0.46–0.94] | 2.16 [1.82–2.91] |
| ABS in conventional polyps | 27 | 0.83 | 3.09 |
| ABS in serrated polyps | 18 | 0.45 | 4.00 |

(People counted per object; the figure merges the one DIS/VAL-shared donor, hence 21 ASC people there.)
Within person: ASC stem ≥ own healthy STM in **11 / 11**; SSC stem < own healthy STM in **6 / 7**.
Caveat: ASC was partly defined by stem-like expression in Chen 2021, so the ASC result is a
consistency check; the SSC result (low stem, midway mature) is not built into the labels.
Figure: `figures/fig14_stem_mature.png`.

### Talk figures (`scripts/make_story_figures.py`, login node, seconds)

`fig11_one_person_map.png` (HTA11_6801 own map), `fig12_no_lookalike.png` (DIS, polyp cells with
≤ 5 % healthy neighbours), `fig13_person_clumps.png` (DIS, healthy vs polyp cells coloured by
person; medians 0.33 → "3 in 10", 0.73 → "7 in 10"), `fig14_stem_mature.png`.

## 2026-10-22 — Visium: polyp vs normal spots from textbook marker genes (job 332760)

`sbatch scripts/visium_marker_calls.sh` → `derived/visium/marker_calls_{spots.tsv.gz,summary.tsv}`,
`figures/fig15_visium_marker_calls.png`. Fixed literature sets (not our DE): conventional = Wnt
targets AXIN2, LGR5, ASCL2, NKD1, SOX9, MYC; serrated = MUC5AC, TFF1, TFF2, ANXA10, AQP5, CLDN18;
mature = CA1, AQP8, CLCA4, SLC26A3, GUCA2B, MS4A12. Mean log-normalised expression per set,
z-scored over mucosa spots of all 7 captures; polyp if max(z_conv, z_serr) − z_mature > 0; route
of a spot = larger of z_conv, z_serr. Scored on adenoma / adenoma_border / normal_mucosa spots only.

| Section | Type | Lesion / normal spots | Lesion called polyp | Normal called normal | Agreement | κ | AUC polyp score | AUC smoothed (19 nn) | Route call (share of called polyp spots) |
|---|---|---|---|---|---|---|---|---|---|
| 7319_2 | SSL/HP | 1000 / 0 | 66.9 % | — | — | — | — | — | serrated (91.9 %) ✓ |
| 7319_3 | SSL/HP | 714 / 0 | 61.3 % | — | — | — | — | — | serrated (73.1 %) ✓ |
| 7319_4 | TA/TVA | 1312 / 0 | 96.4 % | — | — | — | — | — | conventional (99.2 %) ✓ |
| 8270_1 | TA/TVA | 377 / 388 | 53.3 % | 68.3 % | 60.9 % | 0.22 | 0.66 | 0.76 | conventional (95.0 %) ✓ |
| 8270_2 | TA/TVA | 291 / 123 | 44.7 % | 74.0 % | 53.4 % | 0.14 | 0.57 | 0.62 | conventional (98.5 %) ✓ |
| 8270_3 | SSL/HP | 539 / 253 | 84.8 % | 32.4 % | 68.1 % | 0.19 | 0.63 | 0.71 | serrated (84.2 %) ✓ |
| 8270_5 | SSL/HP | 86 / 143 | 82.6 % | 67.1 % | 72.9 % | 0.46 | 0.82 | 0.92 | serrated (91.5 %) ✓ |

Per-set AUC (lesion vs normal): conventional set 0.59 / 0.64 on TA sections; serrated set 0.60 /
0.95 on SSL sections; mature set lower in lesion only weakly (0.46–0.64). Smoothing = mean polyp
score over each spot's 19 nearest spots (same section), threshold 0: accuracy 57–82 %.

Positive: the route of every slice is recovered, 7 / 7. Negative: spot-level polyp vs normal is
weak to moderate (agreement 53–73 %, κ 0.14–0.46), weakest on the one scRNA-shared donor
(8270_2). Notable: on SSL section 8270_3 the pathologist's normal mucosa scores high on the
serrated set (mean z 0.43 vs lesion 0.72), so 68 % of its normal spots are called serrated —
field effect, proximal-site baseline or annotation; not resolvable here.

### Authors' per-spot fields as polyp-vs-normal separators (ST_master `obs`; AUC lesion vs normal)

| Section | SSC program | STM program | ABS program | cnv_score |
|---|---|---|---|---|
| 8270_1 (TA) | 0.48 | 0.44 | 0.40 | 0.46 |
| 8270_2 (TA) | 0.60 | 0.46 | 0.58 | 0.46 |
| 8270_3 (SSL) | 0.59 | 0.37 | 0.45 | 0.54 |
| 8270_5 (SSL) | 0.85 | 0.15 | 0.60 | 0.44 |

No ASC program column in these files. Negative: the published scRNA-derived scores and the CNV
score do not separate polyp from normal spots better than the textbook markers (fig15).
`obs["Variants"]` is a per-section constant (bulk WES count), not per spot.

### Correction (2026-10-22): Visium donors in our single-cell data

The 10-19 line "HTA11_10711 is the only Visium polyp donor also in our scRNA" is wrong (zero-padded
IDs in Visium, e.g. `HTA11_07862` vs scRNA `HTA11_7862`). With leading zeros stripped, all 6 donors
are present (`derived/pseudobulk/*_cells.tsv.gz`):

| Captures | Donor | scRNA object | scRNA polyp cells | scRNA normal cells |
|---|---|---|---|---|
| 7319_2, 7319_3 | HTA11_08622 | VAL | 2,488 (SSL) | 2,999 |
| 7319_4 | HTA11_01938 | DIS | 2,178 (TVA) | 202 |
| 8270_1 | HTA11_07862 | VAL | 857 (TA) | 1,641 |
| 8270_2 | HTA11_10711 | VAL | 473 (TA) | 0 |
| 8270_3 | HTA11_07663 | VAL | 2,048 (SSL) | 2,993 |
| 8270_5 | HTA11_06134 | DIS | 487 (HP) | 496 |

## 2026-10-23 — Next step 1: removing the person effect with scVI (job 338312)

`sbatch scripts/person_free.sh` → `derived/person_free/` (`person_free_metrics.tsv`, latents, UMAP
table), `figures/fig18_person_free_{DIS,VAL}.png`. Healthy + conventional + serrated cells, 2,000
HVG, scVI (2 layers, 10 latent, NB, 300 epochs). kNN k=30. "Same person" for healthy cells is
counted among healthy cells only, and for polyp cells among polyp cells only. So the PCA row
differs from the 10-22 label-free table, which counted neighbours among all cells.
Means over cells:

| Object | Embedding | Healthy: same-person nbrs | Polyp: same-person nbrs | ASC/SSC: same-label nbrs | All labels agree | ASC/SSC: healthy nbrs |
|---|---|---|---|---|---|---|
| DIS | PCA, no correction | 0.45 | 0.72 | 0.99 | 0.87 | 0.029 |
| DIS | scVI, no person key | 0.57 | 0.80 | 0.98 | 0.85 | 0.021 |
| DIS | scVI, person removed | **0.30** | **0.39** | 0.95 | 0.84 | 0.033 |
| VAL | PCA, no correction | 0.51 | 0.68 | 0.97 | 0.87 | 0.022 |
| VAL | scVI, no person key | 0.71 | 0.83 | 0.97 | 0.86 | 0.011 |
| VAL | scVI, person removed | **0.28** | **0.50** | 0.95 | 0.85 | 0.044 |

Chance: same person 0.07 (healthy) / 0.08 (polyp); ASC vs SSC same label 0.56 (DIS) / 0.54 (VAL);
all labels 0.31 / 0.33.

- Removing the person roughly halves the same-person share for healthy cells (0.45→0.30,
  0.51→0.28) and for polyp cells (0.72→0.39, 0.68→0.50). ASC and SSC stay apart (0.95 vs
  chance 0.55) and almost never neighbour healthy cells (≤ 4.4 %). In the corrected map,
  ASC and SSC form one island each in both objects (fig18, bottom right). Without correction
  they form several person-sized islands.
- Negative: healthy cells still have 4× chance same-person neighbours after correction.
  scVI *without* the person key clumps by person more than plain PCA (0.57 / 0.71), so the
  gain comes from the person key, not from the VAE itself.
- The polyp same-person share stays above the healthy share after correction (0.39 / 0.50 vs
  0.30 / 0.28). This is consistent with real per-polyp clonality, but person and processing batch
  are the same thing here, so the data cannot separate the two.

## 2026-10-23 — Next step 2: polyp as the odd one out (job 338313)

`sbatch scripts/polyp_anomaly.sh` → `derived/anomaly/` (`anomaly_people.tsv`, `anomaly_states.tsv`,
`anomaly_cells_{DIS,VAL}.tsv.gz`), `figures/fig19_anomaly.png`. Leave-one-person-out, 33
person × route tests (18 conventional, 15 serrated; HTA11_6801 counted under both). Each test
trains on other people's healthy cells only (≤ 30,000; HVG chosen on them). Score = mean
distance to the 15 nearest training healthy cells. AUROC = the held-out person's polyp cells vs
their own healthy cells.

| Score | Route | Median AUROC (min) | People > 0.7 | New cells vs other polyp cells, median AUROC | Top-10 % that are new cells vs base share (medians) |
|---|---|---|---|---|---|
| scVI latent | conventional | 0.66 (0.26) | 6 / 18 | 0.56 (ASC) | 0.27 vs 0.29 |
| scVI latent | serrated | 0.73 (0.48) | 8 / 15 | **0.91 (SSC)** | 0.56 vs 0.22 |
| PCA | conventional | 0.69 (0.33) | 8 / 18 | 0.67 | 0.40 vs 0.29 |
| PCA | serrated | 0.78 (0.41) | 8 / 15 | 0.79 | 0.29 vs 0.22 |
| no look-alike (fig10; not held out) | conventional | 0.97 (0.53) | 17 / 18 | 0.75 | 0.51 vs 0.29 |
| no look-alike (fig10; not held out) | serrated | 0.97 (0.68) | 14 / 15 | 0.85 | 0.51 vs 0.22 |

Median score per state, as the share of the person's own healthy cells scoring lower (scVI;
`anomaly_states.tsv`): SSC 0.99 in serrated and 0.96 in conventional polyps; ASC 0.82 / 0.85; EE
0.89 / 0.97; TAC 0.80 / 0.80; polyp ABS 0.62 (conventional) vs 0.79 (serrated); polyp STM
0.67 / 0.55.

- A model that never saw the held-out person separates their polyp from their healthy lining
  only moderately (median 0.66–0.78). The deep model does not beat PCA.
- SSC is the most "unlike healthy" state in the data (0.99). ASC is not: inside conventional
  polyps it scores like the other polyp cells (AUROC 0.56). This fits ASC being stem-like (fig14):
  healthy crypts contain stem cells, so ASC has healthy look-alikes in other people.
- Negative: 4 conventional and 2 serrated tests are at or below 0.55 (scVI). Several of them are
  polyps with almost no new cells: HTA11_7469 (ASC 0.1 %, AUROC 0.26), HTA11_83 (SSC 0.1 %, 0.48),
  HTA11_5216 (SSC 0 %, 0.53), HTA11_6801 conventional (ASC 6 %, 0.48).
- The "no look-alike" score reaches 0.97, but it is not a held-out test. It was computed on the
  map that contains the person's own healthy cells, and those are the healthy neighbours it counts.
  It shows the separation exists within a person; it does not show that it transfers to a new one.
  Early stopping never triggered (150 / 150 epochs in every fold).

## 2026-10-23 — Next step 3: a flow from healthy to polyp (job 338315)

`sbatch scripts/polyp_flow.sh` → `derived/flow/` (`flow_people.tsv`, `flow_summary.tsv`),
`figures/fig20_flow.png`. Leave-one-person-out, 33 person × route tests. Space: 30 PCs, refit
per fold on the training people. Training pairs: one-sided entropic OT from each training person's
healthy cells to their own polyp cells. Every polyp cell must be reached; healthy-cell mass is free
(KL, rho = 1), and that free mass is the growth weight. Flow matching (MLP, 4,000 steps) plus a
growth MLP. Each prediction starts from the held-out person's healthy cells (≤ 1,500). Score =
energy distance to their real polyp (≤ 1,500 cells), lower is better.

| | Conventional (18) | Serrated (15) | Both (33) |
|---|---|---|---|
| Median distance: identity (healthy unchanged) | 0.293 | 0.316 | 0.304 |
| Median distance: mean shift | 0.204 | 0.196 | 0.203 |
| Median distance: population (other people's polyps) | **0.172** | **0.165** | **0.171** |
| Median distance: flow | 0.240 | 0.235 | 0.238 |
| Median distance: flow + growth | 0.245 | 0.244 | 0.244 |
| Flow + growth closer than identity | 12 | 11 | 23 |
| … closer than mean shift | 7 | 7 | 14 |
| … closer than population | 2 | 6 | 8 |
| Right-route prediction closer than wrong-route | 14 | 11 | 25 |

- The flow moves healthy cells toward the person's real polyp (beats "unchanged" in 23 / 33;
  20 / 21 among people whose polyp has ≥ 10 % new cells). It also picks the right route: the
  right-route prediction is closer than the wrong-route one in 25 / 33.
- **Negative:** the flow does not beat simply taking other people's polyp cells (8 / 33). It does no
  better than shifting every healthy cell by the training average (14 / 33). The growth term adds
  nothing (flow + growth closer than flow alone in 11 / 33). Starting from a person's own healthy
  cells does not yet help predict their polyp.
- **Negative:** predicted new-cell shares (ASC / SSC by a kNN on the published labels) do not follow
  the real ones (Pearson r = −0.29 conventional, −0.47 serrated; fig20 right). Flow predictions
  stay near 0.05–0.35 regardless of truth. The population baseline also has negative r (−0.50 /
  −0.80). That is a leave-one-out artefact: removing a person with many new cells lowers the
  remaining pool's share.
- HTA11_6801 (both routes): distance to the real TA 0.169 (right route) vs 0.270 (wrong); to the real
  SSL 0.135 vs 0.301. Population: 0.173 / 0.073.
- Polyps with almost no new cells are where every model fails against "unchanged". Examples:
  HTA11_7469 (0.1 % ASC) identity 0.088 vs flow 0.525; HTA11_83, 7862, 5216, 10167, 6025 likewise.
  These polyps are close to their own healthy lining. A flow trained mostly on polyps that changed
  a lot over-changes them.

## 2026-10-23 — Next step 4: single cells placed onto the Visium slices (job 338316)

`sbatch scripts/visium_mapping.sh` → `derived/visium_mapping/` (`mapping_summary.tsv`,
`mapping_by_annotation.tsv`, per-spot `props_*`), `figures/fig21_visium_mapping.png`. DestVI
(CondSCVI 300 epochs on the reference, DestVI 2,500 epochs on in-tissue spots). 7 captures × 2
references. **same** = the person's own epithelial cells, topped up for states with < 25 own cells,
plus pooled non-epithelial cells. Own cells make up 13–74 % of the reference. **other** = other
people only.

| Capture | Route | Ref | ASC in adenoma spots | SSC in adenoma spots | ASC vs SSC call | AUC new cells, adenoma vs normal spots | Marker-gene AUC (10-22) |
|---|---|---|---|---|---|---|---|
| 7319_2 (8622) | serrated | same / other | 0.015 / 0.010 | 0.265 / 0.324 | ✓ / ✓ | no normal spots | — |
| 7319_3 (8622) | serrated | same / other | 0.033 / 0.000 | 0.263 / 0.313 | ✓ / ✓ | no normal spots | — |
| 7319_4 (1938) | conventional | same / other | 0.121 / 0.222 | 0.088 / 0.163 | ✓ / ✓ | no normal spots | — |
| 8270_1 (7862) | conventional | same / other | 0.189 / 0.000 | 0.064 / 0.000 | ✓ / none | 0.62 / 0.47 | 0.66 |
| 8270_2 (10711) | conventional | same / other | 0.076 / 0.000 | 0.000 / 0.000 | ✓ / none | 0.66 / 0.54 | 0.57 |
| 8270_3 (7663) | serrated | same / other | 0.034 / 0.022 | 0.233 / 0.301 | ✓ / ✓ | 0.64 / 0.57 | 0.63 |
| 8270_5 (6134) | serrated | same / other | 0.000 / 0.000 | 0.002 / 0.364 | none / ✓ | 0.85 / 0.92 | 0.82 |

"none" = both ASC and SSC ≈ 0 in adenoma spots, so the call is not informative.

- The route is read correctly from which polyp-only cell type the adenoma spots contain: 6 / 7
  captures with the same-person reference, 5 / 7 with other people's cells. With the other-people
  reference, ASC is never placed in captures 8270_1 or 8270_2. The person's own ASC cells are needed
  to find ASC in their tissue (ASC 0.19 vs 0.00 and 0.08 vs 0.00).
- Adenoma vs normal spots by polyp-only share: same-person reference 0.62–0.85 (higher than the
  other-people reference in 3 / 4). This is about the same as the marker-gene scores of 10-22
  (0.57–0.82), so it is not clearly better.
- **Negative — specificity:** normal-mucosa spots are not free of polyp-only cells. Healthy pieces
  get SSC 0.15 (8270_3, a separate tissue piece) and ASC 0.08 (8270_1). Plasma cells dominate
  normal mucosa (0.15–0.53).
- **Negative — spread:** in the two captures where normal lining touches the polyp, normal spots
  next to the polyp do not carry more polyp-only cells. 8270_2: within 3 spot-widths 0.0003 vs
  beyond 10 0.029, Spearman ρ(distance, share) = −0.17, p = 0.06, the opposite of spread.
  8270_5 has 4 far spots, too few to test. No support for "the lining next to a polyp already
  carries its change".
- No smooth-muscle reference cells exist. Muscle spots are filled with plasma cells, fibroblasts
  and SSC (SSC 0.07–0.13 in 7319_2 / 7319_3 / 8270_3 muscle).
