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

## 2026-10-20 — Simplified background slide

Reworked the background slide as a two-branch diagram: normal colon → conventional or
serrated polyp → possible cancer. APC and BRAF are introduced in plain language as a
growth-brake gene and part of a growth signal, with brief gray definitions. Added the
feasibility answer explicitly: the current core uses established methods; the challenge
is their careful application to paired donors and two routes. Arrows are labeled as
possible routes, not observed progression, because the data are cross-sectional.

## 2026-10-20 (later) — Deck rebuilt as a story; feasibility answer reversed to "yes, one new tool"

Owner instruction (Yuqi): the background slide was not intuitive; APC/BRAF and other
jargon must go; slides should tell a story in plain words, numbers only when instantly
meaningful, a gray one-line explanation under any new term, most explanation on the
approach, concise results. Story order fixed as: problem → data and its surprise →
current models and why they fall short → proposal and where the signal is → evidence →
what it means. Both rules now live in the `slide-storytelling` skill
(`~/.claude/skills/slide-storytelling/`, linked for Codex and `~/.agents`) and a pointer
in the global agent rules. The "Simplified background slide" entry above is superseded.

Decisions:

- **Eduardo's feasibility question is now answered "yes" for one step.** The 10-19 framing
  ("every step is a standard method; OT optional") is replaced on the slides by: standard
  tools compare groups of people; the question lives inside each person, so we build a
  same-person cell-matching tool (OT between a donor's polyp and normal cells). Steps 1–3
  and 5 stay standard and already run; step 4 is the new tool. OT moves from "optional,
  first in drop order" to the proposed method contribution — see PLAN.md. The standard
  core must still stand without it.
- **The data surprise is donor HTA11_6801** (VAL): a TA and an SSL from the same sigmoid
  colon, each with its own adjacent normal. Normal 0 % ASC / ≤0.1 % SSC; TA 6.4 % ASC,
  1.6 % SSC; SSL 27.1 % SSC, 1.2 % ASC. It is the only two-route donor in the data we hold
  (3 in the full release). Caveat kept in notes: the TA also scores high on the DIS
  serrated-up signature (X3), so it is not a clean conventional lesion transcriptionally.
- **Hypothesis checks X1–X5** (job 327343; results in the report) were chosen to test
  "the route is written in the departure from the donor's own normal":
  X1 own-normal fingerprint, X2 raw vs delta route separation, X3 DIS signatures on VAL
  polyps, X4 which normal state each lesion state resembles, X5 route bias inside fixed
  states. X1, X4 and X5 support the story and are on slides 7, 9, 10. **X2 is negative**:
  subtracting the donor's normal does not improve coarse leave-one-donor-out route calls
  (DIS 17 → 15 / 20, VAL 11 → 11 / 14); in 2,000-HVG space the route is already readable
  from the polyp alone, mostly via ASC/SSC composition. Reading: anchoring removes a donor
  fingerprint (X1) and is needed for the *decomposition*, but it is not shown to sharpen
  route classification. Not on the slides; kept here and in the report.
  X1 caveat: a polyp and its own normal were processed together, so the "fingerprint"
  may partly be handling batch. Either source argues for anchoring.
- X6 submitted (job 327354): paired `~donor + condition` vs unpaired `~condition` DESeq2
  on identical specimens, comparing hits and DIS → VAL replication.
- New plain-language figure `figures/fig8_new_cells.png` (`scripts/make_story_figures.py`):
  DIS+VAL pooled per-person slopes, no cohort/state codes.
- Cited on slides (all verifiable): Fearon & Vogelstein 1990 Cell; Snover 2011 Hum Pathol;
  Chen et al. 2021 Cell; Lee-Six et al. 2019 Nature (~1 % of normal crypts in middle age
  carry driver mutations); GLOBOCAN 2020 (~1.9 M cases, ~0.9 M deaths); serrated pathway
  15–30 % of CRC (slide says "up to 30 %").

Candidate experiments before Thursday's talk (2026-10-22), in priority order:

1. **Cell-level OT pilot of step 4** on 3–5 donors (incl. HTA11_6801): unbalanced Sinkhorn
   in numpy (no POT/moscot in the env) on PCA of a donor's normal + polyp cells; report the
   share of ASC / SSC mass sent to each normal state. Turns slide 9 from a pseudobulk
   preview into a first run of the new tool. ~1 day.
2. X6 pairing benefit (running).
3. Leave-one-donor-out stability of X4 and of the shared / route gene sets.
4. Marker check of the `Cell_Type` labels (the likely first question).
5. Field question: do serrated-route donors' normals already carry SSC traces or a
   serrated-signature lift? Site-confounded; descriptive only.

## 2026-10-20 (night) — Step 4 first run, and what goes on slide 9

Owner said go on the cell-level OT pilot. Implemented unbalanced Sinkhorn in numpy
(`scripts/cell_matching.py`; no POT/moscot in the env) rather than installing packages, so
the run is self-contained. Design choices and why:

- **Abundance correction.** The test run showed raw mass shares are dominated by ABS (the most
  common normal state), so "top target by mass" is uninformative. The slide uses enrichment
  (mass share / target share). Both are in the report.
- **Normal-labelled ASC/SSC excluded as "healthy" targets.** A few cells in normal mucosa
  carry lesion labels; ASC maps onto them when allowed (6 / 14). Reported, but the slide
  question is which *healthy* type the new cells resemble.
- **Positive control** (polyp ABS/GOB/TAC/... → same normal state, 0.81–0.94) is what makes the
  lesion mapping believable; it goes on the slide as "8 in 10".
- **Unbalanced OT's untransported mass** is used as a novelty readout: lesion states are the
  least matched polyp state in 23 / 24 donor-routes. Caveat: rare states (EE, TUF) are also
  poorly matched, so low matching is not unique to lesion states; the claim is relative to the
  donor's other polyp states, as stated.
- **Cross-person comparison is weak** (own normal cheapest in 10 / 33). Not on the slides.
  The cell-level cost may be dominated by composition rather than donor fingerprint.

Result agrees with the pseudobulk preview (X4) and with Chen 2021's origin model, now per
person and per cell: ASC → STM 11 / 14, SSC → ABS 9 / 10, stable over five settings. Slide 9
rewritten as "first run of the new tool"; step 4 chip "new · first run"; closing slide says
"grow the matching tool from first run to full method" (merged onto the owner's own edit of
that slide, which shortened "Next five weeks" to "Next"). The owner also removed Eduardo's name
from the models slide; it stays in the speaker notes.

Marker check done (`scripts/marker_check.py`): labels supported; stem markers are highest in
ASC, then STM — consistent with ASC → STM.

Still open from the candidate list: leave-one-donor-out stability of the route gene sets; the
field question. For the matching tool: a real leave-one-donor-out and a shuffled-label null
for the enrichment.

## 2026-10-22 — Deck: cover pictures, real polyp tissue on slide 2, models slide reframed

Owner request on the midterm deck (artifact version 38).

- **Slide 4 (models) reframed.** Owner: the mutation ladder is shared by both routes, so it
  goes on the left and branches into the two routes. Conventional card keeps the stem-cell
  story (stem cells divide all the time; the first break jams their off switch). Serrated card
  says it starts in mature cells (a growth switch stuck on wakes resting surface cells, then
  many genes go silent). Gray term lines for "stem cell" and "mature cell". The constraints
  stay as one strip underneath, with the owner's wording for the closing line. Framing note:
  Fearon & Vogelstein's ladder is the conventional APC→KRAS→TP53 sequence; "both routes climb
  a ladder" is the general step-by-step model, with the serrated steps from Snover 2011
  (BRAF, then CpG-island silencing). Speaker notes carry the specific genes.
- **Slide 2 (polyp).** Added two real H&E tissue slices from our Visium data under the drawn
  figure: 8270_1 (HTA11_07862, TA/TVA) and 8270_5 (HTA11_06134, SSL/HP), both sigmoid, two
  different people — not the HTA11_6801 two-route donor, who has no Visium capture. Dashed
  outline = pathologist `adenoma` + `adenoma_border` spots. Drawing compressed vertically
  (410 px) to make room; numbers unchanged. Script: `scripts/make_he_panels.py`.
- **Slide 1 (cover).** Two colonoscopy photos (conventional on a stalk; serrated) and the NIH
  BioArt crypt drawing (stem cells at the bottom), which sets up slide 4's stem-vs-mature
  split. All Wikimedia Commons, CC BY / CC BY-SA, credited on the slide; licences in
  `presentation/midterm_deck/images/CREDITS.md`. The CC0 adenoma–carcinoma diagram on Commons
  was rejected: gene names on the slide break the plain-words rule.
- A page save (version 37, the `data` slide retitled "Two polyps took two different routes")
  landed while these were built; the three replaced slides were taken from the live version
  read before it, so any page edits to cover/polyp/models in that window would be lost.
- Modality check for the owner: in hand and used are scRNA-seq (CELLxGENE DIS/VAL + OSF
  abnormal epithelium) and Visium spatial RNA (7 OSF polyp captures with H&E). In hand but
  unused: OSF WES MAF (97 samples, only 12 polyps). Open but not downloaded: Synapse Bulk DNA
  L3 VCFs, MxIF / H&E images (CRDC), CODEX and GeoMx DSP (both carcinoma-only). No ATAC in
  HTA11. Inventory: `record/005_open_access_audit/hta11_access_summary.tsv`.

## 2026-10-22 (later) — Slide 3 as a dataset table; cell-count correction; QC stance

- **Correction.** Slide 3 said "33 people each gave a polyp and their own healthy lining,
  about 120,000 cells". 122,811 is every epithelial cell in DIS + VAL (55 people, incl.
  unpaired and CRC specimens). The 33 paired people (DIS 20, VAL 13; HTA11_6801 paired for
  both routes) carry 53,292 + 39,779 = **93,071** cells. Slide now says "about 93,000".
  Source: `derived/pseudobulk/{DIS,VAL}_specimens.tsv`.
- **Checked, unchanged.** HTA11_6801 (VAL, all sigmoid): conventional (TA) ASC 65/1,014 =
  6.4 %; serrated (SSL) SSC 342/1,264 = 27.1 %; two normals 1 SSC in 1,689 cells (shown as
  0 %). Source: `VAL_composition.tsv`.
- **Slide 3 layout.** Table (single-cell RNA; tissue slices) with what we have and what each
  is for, source line, then the one-person surprise as three compact cards, and a one-line
  quality footer. Owner's title kept.
- **QC stance, as applied today.** Upstream: the authors kept high-quality barcodes with
  dropkick (CELLxGENE collection description). Ours: no extra cell filter; pseudobulk sample
  needs ≥ 30 cells (all-epithelium or per state); donor kept only if both normal and polyp
  survive; genes need ≥ 10 counts in ≥ 3 samples; DESeq2 with Cook's refit; matching uses
  healthy types with ≥ 20 cells. Open: DIS median mito 37–44 % per specimen (VAL 25–28 %).
- **Decision: no QC slide in a 3–5 min talk.** One footer line on slide 3 plus speaker
  notes; the mito question is answered verbally if asked. Reason: the story order gives
  method detail to notes, and QC does not move the argument.
- The deck was being edited in the page during this change (versions 38 → 87); `data.html`
  was replaced on top of a page save made less than a minute earlier.

## 2026-10-22 — Label-free map for the deck (job 332524)

- **Question (owner):** do we have the most direct look at the data — our own UMAP/PCA from the RNA
  with nothing done to it — where some cells visibly differ? `fig1_umap.png` used the authors'
  published embedding (`obsm/X_umap`), so it was not that.
- **What "nothing done" can mean:** raw-count PCA is dominated by sequencing depth, so the minimum
  is depth normalisation + log + variable genes. No batch correction and no labels, which is the
  claim we can make on a slide. Labels are painted on only after the map is built.
- **Added a label-free "healthy look-alike" measure** (share of 30 nearest cells from healthy
  lining). It defines polyp-only cells without the atlas labels and recovers 88–97 % of ASC/SSC.
- **Reading:** polyp cells cluster by person much more than healthy cells (median 0.67–0.73 vs
  0.33–0.40 same-person neighbours). Plausible as clonal outgrowth (each polyp descends from few
  cells) or as sample handling; we cannot separate the two here. It is consistent with X1.
- **Deck suggestion, not applied:** the one-person map (HTA11_6801) is the cleanest direct picture
  and fits the slide-3 surprise; the DIS triptych is a backup. PCA plot not recommended.
- **Owner decision (2026-10-22 ~03:00):** do items 1, 2, 3 and 5 of the proposed visualizations;
  translate every cell-type code into plain words; **all data results go on slide 5 onward** (the
  owner's part of the talk). So the one-person map goes on a new first-look slide in the evidence
  block, not on slide 3. Slide 3's existing 0 % / 6 % / 27 % cards were left as they were; asked
  the owner whether they should move too.
- **Deck changes (v119, 13 slides):** new `look` slide before Evidence 1 (one-person map +
  everyone's no-look-alike map; one gray term line for "map"); `person` slide swaps the square grid
  for the map coloured by person beside the 21 / 36 vs about 2 numbers; `newcells` caption adds
  "our label-free map finds 9 in 10 of them"; new `genes` slide after `resemble` (stem vs mature
  genes, 11 of 11 / 6 of 7). Section s5 now starts at `look`. Item 4 (matching arrows) not done.
- **Why the stem/mature check is framed as "a second check":** it reads the cells' own genes with
  no matching, so it backs Evidence 3 independently of the OT tool. The circularity for ASC (labels
  partly stem-defined) is stated in the speaker notes, not on the slide.
- **Time risk:** 13 slides in 3–5 min. Suggested if over time: drop `genes` or merge `look` into
  the spoken intro of Evidence 1.

## 2026-10-22 — Owner questions: spatial trajectory, ATAC/MxIF, Chen 2021 boundary

- Checked Chen 2021 full text (Europe PMC, PMC8941949) for what it already claims; summary now in
  `KNOWLEDGE.md`. Consequence: cell-of-origin (stem vs differentiated), top-down vs bottom-up in
  tissue, and ASC/SSC trajectories are Chen's. Our slides must frame `resemble` and `genes` as
  "holds inside each person", citing Chen. Not yet edited in the deck; raised with the owner.
- Spatial: reproducing top-down / bottom-up on Visium would repeat Chen's MxIF result at worse
  resolution (55 µm spots; 7 polyp captures; 1 donor shared with scRNA). Proposed instead: use the
  polyp-to-normal border inside one section as a same-person spatial pair (does nearby normal
  already carry the shared change?). Descriptive only, 2 sections per route with normal spots.
- ATAC: none in HTA11; Stanford Becker 2022 only, mostly conventional/FAP, no R on host. MxIF:
  images only; segmentation pipeline needed. Both judged too costly for the remaining ~5 weeks
  unless the owner wants a modality arm; no decision yet.
- **Visium marker annotation (owner request, job 332760).** Literature marker sets fixed before
  running, one global rule for all 7 slices, scored against pathologist labels. Outcome: route per
  slice 7 / 7; spot-level polyp vs normal only 53–73 % agreement. Likely reasons: Wnt/stem markers
  are also on in normal crypt bases, a 55 µm spot mixes crypt base and top, and mature genes drop
  only weakly at spot level. The SSL slice 8270_3 has serrated-marker signal in "normal" mucosa —
  candidate for the field-effect question raised earlier. Kept as a descriptive panel, not a slide
  yet; offered to the owner.

## 2026-10-22 — Owner idea: landmark SNVs + scRNA-corrected spatial; data map

- **Idea (owner):** rediscover non-textbook, patient-specific SNVs; use scRNA as knowledge to
  impute/correct Visium; annotate polyp vs normal on the corrected spatial data.
- **Checked:** Visium chemistry `Spatial 3' v1` (fresh frozen); scRNA TruDrop; we hold counts
  only, no reads (Level 1/2 behind dbGaP). Bulk WES MAF exists for all 7 Visium polyps (OSF).
  Authors' per-spot CNV score: AUC 0.44–0.54 lesion vs normal; their scRNA-derived NMF scores:
  SSC 0.48–0.85 (results in the report).
- **Assessment given to owner:** SNV part not feasible on held data (no reads; 3' tags and
  ~1,300 UMIs per spot give ~0–1 reads per SNV per spot even with reads; dbGaP takes longer than
  the remaining weeks) and largely prior art (Chen DENDRO scRNA-SNV phylogeny; Heiser WES + Visium
  CNV clones). scRNA→spatial deconvolution (Tangram / cell2location / RCTD) is feasible in days
  but established, and the same-person reference exists for 1 of 7 sections only. Suggested a
  short deconvolution test as an annotation baseline, not as the project's novelty.
- Wrote `START.md` (data and code map) on the owner's request to understand data scale/storage.

## 2026-10-22 — Owner steer: course project, future direction only; spatial slide

- **Owner:** this is a course project — deploying an idea and generating results is enough; no
  need to be novel. Tomorrow's talk only *introduces* a potential future (scRNA-guided spatial,
  person-specific landmarks such as mutations); no feasibility analysis needed now. Wants at least
  one spatial figure in the deck.
- **Deck v120 (14 slides):** new `tissue` slide (Evidence 5) after `programs`: the two slide-2
  slices with spots coloured by their route's textbook genes (fig16; Wnt set on 8270_1 whole slice,
  stomach-like set on 8270_5), dashed pathologist outline, "7 of 7 slices: the genes name the right
  route". Notes say spot-level border agreement is only ~2 in 3. `meaning` Next line now ends with
  the future direction; notes say mutation calls would need controlled raw reads.

## 2026-10-22 — Deck simplified, slides 5+ (v121, 11 slides)

- **Owner request:** keep slides 1–4; simplify the rest. Message: simple signals already show
  preliminary conclusions that match the textbook (not novelty). Put spatial and single cell side
  by side. Short, easy future-work slide. White background, plain format, fewer words, almost no
  gray explanation lines, no colour-bar boxes. Owner asked whether p6 (steps) was redundant.
- **Done:** `steps` removed (its three moves folded into `idea`: compare / split / match, then
  "do the simple signals agree with the textbook?"); `resemble` + `genes` merged into one slide
  (matching table + stem/mature scatter + one textbook line); `programs` + `tissue` merged into one
  single-cell vs tissue slide per route (fig16), 7 of 7 and 97–99 % in one line; `meaning` rewritten
  as "So far, simple signals already show both routes. Next:" with three items. Removed eyebrow
  labels, boxes and border bars; every section `background:#ffffff`. Dropped from slides (kept in
  notes or report): 87–100 % within-state, 8 in 10 positive control, 23 of 24, 5 of 5 settings,
  4 of 4 AUC slices, Know/Use/Reuse.

## 2026-10-22 — Correction: same-person single cells exist for every Visium slice

- Found while choosing example people: Visium donor IDs are zero-padded. All 6 Visium donors are in
  our scRNA, 5 with their own normal. My earlier statements "same-person reference exists for 1 of 7
  sections only" (record, this week) and "only HTA11_10711 overlaps" (KNOWLEDGE, 10-19 report) were
  wrong; corrected in KNOWLEDGE and the report. Consequence: the future plan "use each person's own
  single cells to sharpen their tissue map" is directly runnable on 6 of 7 captures.

## 2026-10-22 — Deck v141 (13 slides): test design, labels explained, person explorer, spatial plan

- **Owner asks:** (1) p5 should say how single cells help spatial and what we expect; (2) p6 says
  "no labels" — where do polyp labels come from? (3) p7 not intuitive — pick one person and
  highlight their normal and polyp, maybe as an artifact; (4) "textbook genes" never explained —
  explain the first-test design; (5) future work must cover our discussion, with a concrete plan
  for single cells → spatial.
- **Done:** `idea` gains step 4 (check in the tissue) and keeps the owner's added line;
  new `tests` slide (table: test / what we use / textbook expects, with example genes; sets fixed
  before looking); `look` says colours are the sample record (polyp vs healthy biopsy) added after a
  genes-only map; `person` uses fig17 (two people highlighted) and links the new **Polyp
  Fingerprint Explorer** artifact (https://claude.ai/artifact/Xi6uWPxrpUKZcgz9LL3YDH; built by
  `scripts/make_person_explorer.py` from `presentation/person_explorer/template.html`), keeps the
  owner's last line; `meaning` points to the plan; new `plan` slide (reference → unmix → map →
  field-effect question; ready on all 6 slice donors).
- Owner had edited slides 1–5 and 7 in the page (v1792630063); merged onto that version. Repo
  mirror now includes the owner's page edits to slides 1–4.

## 2026-10-22 — Slide 3 data sizes; roadmap drift and feasibility talking points for Eduardo

- **Slide 3 (`data`, deck v173):** single-cell row now leads with the atlas total, about 123,000
  lining cells (122,811 epithelial, 55 people), then the 93,071 paired cells from 33 people.
  Spatial row names the technology, 10x Visium, and adds about 6,900 spots (6,915 tissue spots
  over 7 captures, counted from `derived/visium/spots_*.tsv.gz`). Notes add Visium fresh-frozen
  Spatial 3' v1, 55 µm spots, single-cell TruDrop, and the 10,696 unused non-epithelial cells.
- **Submitted roadmap (`ROADMAP_CONCISE.md`) versus what we now run.** Same question and same
  paired, per-route design. Changes: paired people 28/21 → 19/15 as measured in the objects we
  hold (Synapse objects blocked); MxIF dropped because the OSF segmented tables are empty, and
  Visium is the tissue arm (all 6 slice donors are also in the single-cell data); "OT to find
  the coupling" inside the expression test → pairing comes from DESeq2 `~ donor + condition`,
  and OT moves to a separate step, same-person cell matching; "build a model to select marker
  genes" → a marker is a gene that is significant, route-specific, replicated in VAL and
  consistent across donors, then checked on Visium; exome extension parked.
- **Feasibility reading:** the three roadmap items that needed new methods were the ones
  instructors flagged. Two were replaced by standard tools; one (cell matching) is kept as the
  single new step, with a first run done and the standard core standing without it. Talking
  points given to the owner in the session; not a submission text.

## 2026-10-23 — Deck: last slide becomes four next models

- Owner rewrote the deck's closing direction; `plan` (last slide) now lists: (1) a VAE-style
  model that removes the person effect, judged by healthy cells mixing while ASC/SSC stay
  apart (person clumping of polyp cells may be partly real clonality, and batch cannot be
  separated from donor); (2) polyp as anomaly detection against healthy, scored by
  leave-one-person-out AUROC; (3) a healthy→polyp flow/ODE per route that must create the
  new cell types (unbalanced OT / growth term, extends step-4 matching; HTA11_6801 has both
  routes; snapshots, not time); (4) single cells imputed onto Visium to map polyp spread.
- Directions only, per the course scope; caveats live in the speaker notes. The old
  deconvolution plan is folded into item 4. Owner removes `meaning` themselves.

## 2026-10-23 — The four next-step models: implementation design

Owner: "the four plans in Next can start being implemented." AI-implemented; all four run on
`cscc-gpu-p` (scvi-tools 1.3.3 + torch/CUDA 11.8 already in `/l/users/$USER/venvs/hta11`).
Shared loaders in `scripts/next_common.py`. Same cells as the label-free map (healthy +
conventional + serrated, published post-QC cells, no extra filter).

1. **Person-free model** — `scripts/person_free.py` → `derived/person_free/`, fig18.
   Three embeddings per object: uncorrected PCA, scVI without a person key, scVI with
   `donor_id` as batch key. The middle one separates "what the VAE does" from "what removing the
   person does". kNN (k=30) checks: healthy cells' same-person share (should fall to chance),
   ASC/SSC same-label share (should stay high), all-label agreement, ASC/SSC healthy-neighbour share.
   Person = batch here, so the model cannot tell technical from clonal person effects.
2. **Anomaly score** — `scripts/polyp_anomaly.py` → `derived/anomaly/`, fig19.
   Leave-one-person-out: train on other people's healthy cells only (HVG chosen on those too),
   score the held-out person by mean distance to 15 nearest training healthy cells, in an scVI
   latent and, as a no-deep-learning baseline, in a PCA fitted on the training healthy cells.
   Metric = within-person AUROC (polyp vs own healthy), so the held-out person's overall offset
   cancels. Chose latent-density over reconstruction error: per-cell scVI likelihood tracks
   library size. The fig10 "no look-alike" share is carried along as a non-held-out reference.
3. **Healthy→polyp flow** — `scripts/polyp_flow.py` → `derived/flow/`, fig20.
   Step-4 OT made one-sided: every polyp cell must be reached, healthy cells may give more or less
   mass (KL, rho=1) — that mass is the growth weight that lets a few healthy cells make the new
   ASC/SSC. Flow matching (MLP, route as input) on pairs sampled from the coupling; a second MLP
   learns the growth weight. PCA refitted per fold on training people only. Held-out test from
   the person's healthy cells alone vs identity / mean-shift / population baselines (energy
   distance), predicted ASC/SSC share vs real, and right-route vs wrong-route prediction.
   The population baseline is the key one: does starting from a person's own healthy cells beat
   "other people's polyps"? Snapshot caveat stands.
4. **Single cells onto tissue** — `scripts/visium_mapping.py` → `derived/visium_mapping/`, fig21.
   DestVI (scvi-tools; Tangram/cell2location/RCTD not installed, no R). Reference = the person's
   own epithelial cells (states < 25 cells topped up from others so ASC and SSC are always
   offered) + pooled non-epithelial cells; compared with an other-people reference to see whether
   same-person cells help. Checks: ASC+SSC share adenoma vs normal spots (AUC), ASC vs SSC route
   call on 7 captures, and spread = share in normal spots vs distance to the nearest adenoma spot.
   No smooth-muscle reference cells exist; muscle spots are forced into other types.

Each script has `--test`; test jobs 338302–338305 first, then full runs.
