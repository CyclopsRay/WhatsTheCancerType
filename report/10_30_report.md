# HTA11 — Weekly Report, week ending Friday 2026-10-30

Reporting interval: [2026-10-23T18:00:00+04:00, 2026-10-30T18:00:00+04:00) — Asia/Dubai.

Measured results only, with provenance; include positive and negative findings.

## 2026-10-24 — Anomaly score: AUPRC (follow-up to 10-23 "Next step 2")

Follow-up to [10_23_report.md](10_23_report.md), "Next step 2". The score is the same; only the
summary metric is new. AUPRC is average precision (sklearn) with polyp cells as positives, per
held-out person × route. Computed on the login node from `derived/anomaly/anomaly_cells_*.tsv.gz`
→ `derived/anomaly/anomaly_people_auprc.tsv`. Baseline = share of polyp cells among that person's
healthy + polyp cells. A random score scores this on average.

| Route | Tests | Baseline (median) | scVI AUPRC median (min) | PCA | No look-alike (not held out) |
|---|---|---|---|---|---|
| conventional | 18 | 0.42 | 0.58 (0.17); 1.17× baseline; above baseline 16 / 18 | 0.59 (0.11); 1.36×; 15 / 18 | 0.97; 2.21×; 18 / 18 |
| serrated | 15 | 0.43 | 0.65 (0.26); 1.56×; 14 / 15 | 0.62 (0.25); 1.46×; 14 / 15 | 0.95; 2.04×; 15 / 15 |

New cells inside the polyp: positives are ASC in conventional polyps and SSC in serrated polyps,
scored against the other polyp cells. Only tests with ≥ 5 new cells are counted:

| Route | Tests | Baseline (median new-cell share) | scVI | PCA | No look-alike |
|---|---|---|---|---|---|
| conventional (ASC) | 15 | 0.37 | 0.41 (1.08×) | 0.46 (1.34×) | 0.57 (1.49×) |
| serrated (SSC) | 12 | 0.25 | **0.65 (2.55×)** | 0.45 (1.78×) | 0.65 (2.07×) |

- Same picture as the AUROC. The held-out score is moderately above chance and is stronger for
  serrated polyps. It finds SSC well (2.55× baseline) and ASC barely (1.08×).
- Below baseline (scVI): HTA11_6025, HTA11_7469 (conventional) and HTA11_83 (serrated), all with
  few or no new cells. Lowest absolute values: HTA11_104 (0.17 vs baseline 0.05, only 79 polyp
  cells) and HTA11_7469 (0.17 vs 0.26).
- Baselines range from 0.05 to 0.92 across people, because healthy/polyp cell counts differ a lot.
  So compare the lift (AUPRC ÷ baseline), not the raw AUPRC, across people.

## 2026-10-24 — Anomaly v2: reconstruction error of a healthy-only VAE (jobs 341132, 341133)

`sbatch scripts/polyp_recon.sh {hvg,detected}` → `derived/anomaly/recon_*_{hvg,detected}*`,
`figures/fig22_recon_{hvg,detected}.png`. Same leave-one-person-out design as 10-23 (33 tests,
25.8k–30k training healthy cells per fold). scVI 2 × 128, 10 latent, NB, KL warm-up 50, 200
epochs. Genes chosen on training healthy cells only: `hvg` = 2,000 HVG; `detected` = genes in
≥ 0.1 % of them (20.6k–22.2k). Reconstruction error = NB deviance under the posterior-mean
reconstruction, summed over genes, divided by the cell's counts.

**The raw reconstruction error mostly measures depth.** In healthy cells, Spearman ρ(error, total
counts) = −0.94 (DIS) / −0.93 (VAL) for `detected`, and −0.54 / −0.45 for `hvg`. The hidden-layer
distance is not depth-driven (ρ −0.02 to 0.26). DIS SSC cells are deeper than healthy cells
(median 11,022 vs 8,989 counts), so their raw error is *low*. Depth adjustment
(`derived/anomaly/recon_depth_adjusted.tsv`, from saved tables): within each person, regress
log(error) on log(counts) in their own healthy cells and take the residual. Afterwards ρ with
depth ≈ 0. The fit uses the person's healthy cells, which are also the comparison set, so the
adjusted score is calibrated within person, not fully held out.

| Genes | Route | Score | AUROC median (> 0.7) | AUPRC lift over baseline | New cells vs other polyp cells, AUROC |
|---|---|---|---|---|---|
| detected | conventional | error, raw | 0.64 (5 / 18) | 1.29× | 0.58 |
| detected | conventional | error, depth-adjusted | 0.68 (9 / 18) | 1.41× | **0.78 (ASC)** |
| detected | conventional | hidden-layer distance | 0.68 (7 / 18) | 1.19× | 0.66 |
| detected | conventional | mean of the two ranks | **0.71 (10 / 18)** | 1.43× | **0.81** |
| detected | serrated | error, raw | 0.49 (1 / 15) | 0.99× | 0.41 |
| detected | serrated | error, depth-adjusted | 0.60 (3 / 15) | 1.17× | 0.50 (SSC) |
| detected | serrated | hidden-layer distance | 0.68 (6 / 15) | 1.44× | **0.85** |
| detected | serrated | mean of the two ranks | 0.67 (6 / 15) | 1.27× | 0.71 |
| hvg | conventional | error, depth-adjusted / distance | 0.62 / 0.69 | 1.18× / 1.19× | 0.76 / 0.59 |
| hvg | serrated | error, depth-adjusted / distance | 0.54 / 0.73 | 1.10× / 1.56× | 0.42 / 0.89 |

10-23 for reference (KL warm-up never finished): scVI distance 0.66 / 0.73, PCA 0.69 / 0.78.

- The two scores find different new cells. **The reconstruction error finds ASC** (0.78 vs 0.66).
  **The hidden-layer distance finds SSC** (0.85–0.89; error 0.42–0.50). SSC is rebuilt about as
  well as healthy cells but lands far from them in the hidden layer. ASC sits near healthy stem
  cells in the hidden layer, but its genes cannot be rebuilt.
- Neither score separates a new person's polyp from their healthy lining well. The best median
  AUROC is 0.71 (conventional, combined) and 0.73 (serrated, `hvg` distance). Fixing the KL
  warm-up did not change the distance score (0.68–0.73 vs 0.66–0.73 on 10-23), and PCA is still
  as good.
- `detected` vs `hvg`: more genes help the reconstruction error for conventional polyps (0.68 vs
  0.62). They slightly lower the distance score for serrated polyps (0.68 vs 0.73).

Genes the healthy model rebuilds worst in a person's polyp (number of people with the gene in
their top 30 by deviance rise, polyp minus own healthy; `recon_genes_detected.tsv`):
- conventional (18): S100P 13, ID1 12, REG4 10, LINC00486 10, S100A6 8, LCN2 8, REG3A 8, TGFBI 7,
  FABP1 7, REG1A 7, PLA2G2A 7, **NKD1 7**, PITX1 6, DMBT1 6, CEMIP 5, **APCDD1 5**, CEACAM5 5,
  **BMP4 5**.
- serrated (15): S100P 13, **TFF1 12**, REG4 12, S100A6 12, TIMP1 10, HLA-B 9, PITX1 9, MUC2 9,
  ANXA2 8, S100A11 8, **MUC5AC 8**, KRT19 7, **CTSE 7**, AGR2 4.
- Without using any labels, the conventional list carries Wnt targets (NKD1, APCDD1). NKD1 and
  APCDD1 are absent from the `hvg` set by construction. The serrated list carries gastric genes
  (TFF1, MUC5AC, CTSE). Both match the 10-19 route-specific DE genes. Shared top genes (S100P,
  REG4) match the 10-19 shared-up list. Noise: HBB, ACTB, EEF1A1 appear in a few people.
- fig22 plots the **raw** (depth-confounded) error and should not be used as is.

## 2026-10-25 — Progress-report figures (no new analysis)

`scripts/make_report_figures.py DERIVED figures` → `figures/report_fig1–5.png`, used in
`presentation/progress_report/draft_v1.md`. Every number drawn comes from an existing table:

| Figure | Content | Source |
|---|---|---|
| 1 | Pipeline schematic (VAE, unbalanced OT + flow, Visium/DestVI) | synthetic shapes, no data |
| 2a / 2b / 2c | New-cell shares; route-specific genes; DIS→VAL replication | `fig8_new_cells.png`, `fig3_route_compare_DIS_all.png`, `fig4_replication.png` (10-19 / 10-22 runs) |
| 3a | New cells vs other polyp cells, AUROC per person: depth-adjusted error ASC 0.78, SSC 0.50; hidden-layer distance ASC 0.66, SSC 0.85 (medians, detected genes) | `derived/anomaly/recon_depth_adjusted.tsv` (10-24 section above) |
| 3b | Stem vs mature scores | `fig14_stem_mature.png` |
| 4 | Distance to the real polyp: unchanged vs flow + growth vs wrong route; 23 / 33 closer than unchanged, 25 / 33 right beats wrong | `derived/flow/flow_people.tsv` (10-23 report, job 338315) |
| 5 | 4 Visium sections: annotation, marker call, polyp-only share with own vs other reference; AUC own / other 0.62/0.47, 0.66/0.54, 0.64/0.57, 0.85/0.92 | `derived/visium_mapping/props_*`, `mapping_summary.tsv` (10-23 report, job 338316) |
