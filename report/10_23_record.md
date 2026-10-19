# HTA11 — Weekly Record, week ending Friday 2026-10-23

Reporting interval: [2026-10-16T18:00:00+04:00, 2026-10-23T18:00:00+04:00) — Asia/Dubai.

Plans, discussion, decisions, reasoning, and corrections (Chinese or English).

## 2026-10-19 — Instructor feedback on the roadmap, and the plan for the midterm presentation

AI-assisted planning notes for Yuqi Lei and Muhammed Bah. Not submission prose.

### The feedback

7102 instructors, on the roadmap: *"well defined, but I am not sure how feasible. It
seems some steps would require adapting or developing novel analysis approaches.
Please be sure to meet with one of the instructors."*

Deliverables that follow from it:

- **Midterm presentation, 3–5 min**, Tue 2026-10-20 or Thu 2026-10-22 (Fri overflow).
  Must cover: background/motivation, research question, exact data plus initial
  inspection confirming it exists as imagined, specific analyses, **preliminary
  results demonstrating feasibility**, next steps.
- **Progress report**, 3–5 pages, ≤1500 words, ≤5 figures, due **Sat 2026-10-24**:
  title, abstract, introduction, methods, preliminary results, conclusion/next steps.
- Action for the team: book a meeting with an instructor (signup form in the email).

### Reading of "novel analysis approaches"

The submitted concise roadmap leaned on three things that read as method development:
(1) optimal transport "to find the coupling" between normal and polyp cells,
(2) "build a model (end to end, statistic or mix) to select marker genes", and
(3) MxIF segmentation, implicitly. The paired comparison itself is standard. The
response is to **show the standard core running end to end on the real data** and
demote everything novel to optional, after the core:

| Roadmap step | Standard tool | Status after today |
|---|---|---|
| Epithelial states | published `Cell_Type` labels (Chen 2021), incl. ASC / SSC | used as-is; no re-annotation needed for the core |
| Paired state abundance | per-donor proportion deltas, Wilcoxon signed-rank | runs |
| Paired expression | pseudobulk + DESeq2 `~ donor + condition` (PyDESeq2) | runs |
| Shared vs route-specific | LFC comparison + two-sample z on route difference | runs |
| Donor consistency | count of donors agreeing in sign | runs |
| Replication | DIS discovery → VAL validation (donor-disjoint) | runs |
| Pathways | GSEA prerank, MSigDB Hallmark | runs |
| Spatial | Visium polyp captures with pathologist spot annotation, signature scoring | in progress |
| OT correspondence | `moscot` | **optional, not attempted** — the ASC/SSC labels already answer "new vs redistributed" at first pass |
| Marker-gene "model" | — | **reframed**: a marker is a gene that is shared/route-specific, replicated in VAL and consistent across donors. No new model is needed. |

### Arms opened today (tracked on the console artifact)

A1 data inspection; A2 paired composition; A3 paired pseudobulk DE per route;
A4 shared-vs-specific decomposition; A5 VAL replication + donor consistency;
A6 spatial (gate re-check, then Visium scoring); A7 genotype extension (parked);
A8 presentation; A9 progress report.

### Decisions and corrections

- **Spatial gate failed for MxIF, switched to Visium.** All 16 OSF
  `MxIF/quantification/*.csv` files are zero bytes (md5 = the empty-file hash,
  uploaded 2023-11-17). The roadmap's "MxIF shortcut" does not exist; MxIF would
  need whole-slide segmentation from Level-2 images, which is exactly the kind of
  novel pipeline the instructors flagged. Dropped from the plan. The fallback is the
  7 OSF `ST_master` Visium polyp captures, which carry raw counts and a per-spot
  `pathology_annotation` (adenoma / adenoma_border / normal_mucosa / …). Only one
  of their donors (HTA11_10711, TA) is in our scRNA cohort, so the spatial arm is
  descriptive localization, as the roadmap already allowed.
- **Paired donor numbers for the talk: 19 conventional / 15 serrated**, as measured.
  The concise roadmap still says 28 / 21 (full release incl. the Synapse objects).
  Say the measured numbers on the slide.
- **Genotype extension stays parked.** Synapse remains blocked (no credentials on
  this host); OSF `WES/master_depth15_maftools.maf` is the spatial cohort's exomes,
  not our scRNA donors.
- **Not used, noted:** OSF `scRNA/abnormal_epithelium.h5ad` (8,153 malignant /
  lesion epithelial cells, `Tumor_Type` MSS 2,434 / MSI 272 / TA-TVA 454 /
  SSL-HP 389 cells). This partly reopens the carcinoma-subtype question, but its
  `X` is not raw counts and the CRC arm is out of scope.
- **Tooling.** No R on the host, so DESeq2 runs through PyDESeq2 0.5.2 in a new
  project venv `/l/users/yuqi.lei/venvs/hta11` (layers on the promotervi scanpy env).

### 2026-10-19 (later) — What the first run says, and how the talk frames it

Numbers in [10_23_report.md](10_23_report.md). Reading:

- **Feasibility is demonstrated, not argued.** Every core step ran on the real data in
  under 10 min of Slurm time per job, using DESeq2 with donor in the design. Three
  script bugs were fixed on the way (pandas `.attrs` lost on join; duplicate `gene`
  column before GSEA; a Series-and-scalar AND in replication). None affected numbers.
- **The biology is recognisable, which is the point for a midterm.** Conventional-specific =
  Wnt targets (APCDD1, NKD1, ASCL2, MMP7; Hallmark Wnt up in both cohorts); serrated-
  specific = gastric metaplasia (TFF1/TFF2/ANXA1) and TNF-α/NF-κB. Recovering known
  biology is the positive control. It also means the novelty claim has to come from the
  *decomposition with donor-level consistency and replication*, not from the gene lists.
- **Caveat to keep in view:** all-epithelium pseudobulk mixes composition and expression.
  The shared-down set (AQP8, CLCA4, ZG16) is largely the ABS loss. Within-state fits
  exist (ABS/GOB/TAC) but have fewer donors (5–11); the route split per state is the
  next analysis, and the talk says so.
- **Composition p-values are weak by construction** (padj 0.05–0.12; 6–11 donors). The
  slide reports donor counts (16/19, 13/15), which is the honest unit.
- **Route-specific replication is directional, not categorical.** 92–95 % of DIS
  route-specific genes are larger in their own route in VAL, but only 35–44 % re-pass
  the full significance rule — expected at 6–8 donors. A pooled fit is the fix.
- **Visium crossover** is the most persuasive single picture but rests on four sections
  with spot pseudo-replication; framed as descriptive on the slide.
- My earlier guess that the zero-SSC serrated donors were HP was wrong: HP carries SSC.
  Still open.

Talk structure (8 slides, ~35 s each): cover → background/question → data inspected →
analysis plan as standard methods (directly answers the feedback) → result 1 composition
→ result 2 route split → result 3 replication + Visium → next steps and non-claims.
Speaker notes are on each slide. Each student still presents and writes in their own words.
