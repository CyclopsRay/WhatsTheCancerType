# HTA11 — Weekly Record, week ending Friday 2026-10-30

Reporting interval: [2026-10-23T18:00:00+04:00, 2026-10-30T18:00:00+04:00) — Asia/Dubai.

Plans, discussion, decisions, reasoning, and corrections (Chinese or English).

## 2026-10-24 — Anomaly model: a training caveat found while documenting it

While writing out the full anomaly pipeline for the owner, I checked the scvi-tools 1.3.3 defaults.
`n_epochs_kl_warmup` defaults to 400. `polyp_anomaly.py` trains for at most 150 epochs, and early
stopping never fired (150 / 150 in every fold). So the KL weight only ramped linearly from 0 to
≈ 0.375 and never reached 1. The 10-23 anomaly model is therefore a weakly regularised VAE, closer
to a plain autoencoder than standard scVI. The `person_free.py` runs (300 epochs) reached 0.75.
Fix if rerun: `plan_kwargs={"n_epochs_kl_warmup": 50}` (or train ≥ 400 epochs). The 10-23 numbers
stay as reported, but are labelled as coming from this setting.

## 2026-10-24 — Anomaly v2: reconstruction error from a healthy-only VAE (owner's proposal)

Owner proposed three things: (1) a VAE trained on healthy lining only, where polyp cells should
reconstruct badly; (2) distance to healthy neighbours in the hidden layer; (3) whether 2,000 HVG is
too many and the features should be compressed first.

- (2) was already the 10-23 "scVI" score: mean distance to the 15 nearest training healthy cells in
  the 10-d latent. It is kept as `latent`, now with the KL warm-up fixed (50 epochs).
- (3) Checked against the DIS DE tables (`/l/users/$USER/HTA11/tmp/hvg_check.py`, srun). The
  2,000 HVGs picked on healthy cells contain only **16 % of conventional-up and 24 % of
  serrated-up genes** (down-genes 30 % / 25 %). 57 % / 41 % of up-genes are seen in < 1 % of
  healthy cells: APCDD1 0.4 %, NKD1 0.7 %, MMP7 0.8 %, CLDN2 0.2 %. These genes are silent in
  healthy lining and turn on in polyps, which is exactly the anomaly signal, and a
  healthy-variance filter drops them. So the problem is the wrong genes, not too many. The VAE is
  the compression (genes → 10 numbers); compressing with PCA first would make per-gene residuals
  uninterpretable. Decision: keep `hvg` for comparison and add `detected` (≈ 21k genes seen in
  ≥ 0.1 % of training healthy cells). Both are chosen without looking at polyp cells.
- (1) Residual = NB deviance of the cell's counts under its reconstruction (posterior-mean latent,
  observed library), summed over genes, divided by the cell's counts. Dividing by counts stops
  deep cells from scoring high just for being deep. Per test, the 30 genes whose deviance rises
  most from own healthy to polyp are saved; these say which genes the healthy model cannot rebuild.
  A known risk: VAEs can reconstruct out-of-distribution inputs well, so a low error does not
  prove a cell is healthy.
- Script `scripts/polyp_recon.py` (new; `polyp_anomaly.py` kept unchanged for the 10-23 numbers).
  Test 341131 passed. Full runs: 341132 (`hvg`), 341133 (`detected`). In the 3-epoch test, top
  residual genes already included OLFM4, MMP7, REG4, TFF1, MUC5AC. Ambient genes (IGKC, IGHA1,
  HBB) also appear and may need masking.

## 2026-10-24 — Progress report (due today, ≤1500 words, ≤5 figures): proposed figure plan

Proposal for the owner to confirm; students write the prose themselves (KNOWLEDGE.md). Multi-panel
figures count as one figure. Sources are existing files in `figures/`; numbers from
[10_23_report.md](10_23_report.md) and this week's report.

1. Two routes, two new cell types (proposed): (a) H&E for one polyp per route, `fig9_he_*`; (b) the
   new-cell share per person, healthy lining vs polyp, `fig8_new_cells` (16/19, 13/15).
2. Genes: shared vs route-specific + replication — (a) `fig3_route_compare_DIS_all` (224 shared / 53 /
   68); (b) `fig4_replication` (99 % / 97 % same sign in VAL).
3. What the new cells look like in healthy terms — (a) `fig14_stem_mature` (ASC ≥ own STM stem 11/11;
   SSC low stem, mid mature); (b) `fig19_anomaly` right panel (SSC least healthy-like, ASC not).
   The cell-matching result (ASC → own STM 11/14, SSC → own ABS 9/10) stays in the text, since it has no figure.
4. Person effect and held-out polyp detection — (a) `fig18_person_free_DIS`, cropped to the
   no-correction / person-removed rows; (b) `fig19_anomaly` left panel, or fig22 (anomaly v2)
   if jobs 341132/341133 finish in time.
5. Tissue check — `fig15_visium_marker_calls` (route 7/7; spot-level agreement 53–73 %).

Kept to the text as negatives or next steps: flow (fig20; loses to the population baseline 8/33),
DestVI (fig21; no spread signal), X2 (delta does not sharpen route calls).
Caveat for fig19: from the 10-23 run, KL warm-up incomplete (see entry above).

## 2026-10-24 — Progress report intro: do the four next steps each carry meaning? (discussion)

Assessment given to the owner; the owner decides, and the students write the prose themselves.
- (2) Anomaly from a healthy-only model: strongest. It tests Chen 2021's bottom-up vs top-down
  claim without labels. A stem expansion (ASC) should stay inside the healthy distribution, while
  metaplasia (SSC) should not. Measured: SSC 0.99, ASC as in-distribution as the other polyp cells
  (10-23). Closest prior work: Dann et al. 2023 Nat Genet (healthy-reference disease-state detection).
- (1) Person-free scVI: a necessary tool, not a finding. Its place is Methods / the challenge
  paragraph, not a headline. Person and processing batch cannot be separated.
- (4) DestVI / tissue: keep as validation (route 7/7 by markers). Field effect untestable here:
  only 2 sections with adjacent normal tissue, and no spread signal.
- (3) Flow: negative (8/33 vs population). Keep as one tested hypothesis: "a person's healthy
  baseline does not yet predict their polyp beyond the population average". Do not put it in
  the intro's motivation. This also means the intro should not argue "each person's polyp is
  unique". The argument for pairing is noise removal (X1 21/36, about 16 % smaller SE), not
  person-specific polyps.

## 2026-10-24 — Progress report draft v1 (owner's three-step story)

Owner's story: detect polyp cells → predict the polyp from healthy lining → map polyp purity and
route in tissue. Draft at the owner's explicit request, written with the anti-defensive-writing
skill; owner revises by hand: `presentation/progress_report/draft_v1.md` (≈1,380 words in sections;
captions ≈180). Placeholders: anomaly v2 numbers and fig22, Fig 1a schematic, Fig 4 redraw, Fig 5
composite, the OSF source paper, and the serrated-share review.

Framing choices to check (facts unchanged, see the 10-23 report):
- Flow is claimed only as "moves toward the polyp and the right route" (23/33, 20/21 with ≥ 10 % new
  cells, 25/33 right vs wrong). The population baseline (flow beats it 8/33) is not in the figure.
  Next step 2 is phrased as "test whether the person adds information beyond the average polyp".
- The ASC anomaly result is framed by origin (stem-like, so close to healthy stem cells), not as a
  detection miss. The v1 AUROC (0.66/0.73) is not used as a headline.
- The DestVI no-spread result and the X2 negative are left out; spatial is claimed for route and
  purity AUC only.
- Fig 4 is planned as identity / right-route / wrong-route only, replacing fig20.
