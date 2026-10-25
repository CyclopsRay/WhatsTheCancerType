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
- (3) Checked against the DIS DE tables (`/nfs-stor/$USER/HTA11/tmp/hvg_check.py`, srun). The
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

## 2026-10-24 — Storage migration /l/users → /nfs-stor (HPC Phase 2, deadline 2026-10-26)

- Copy made 10-07/08 (`~/migration/migrate.sh`, all `VERIFY OK`). On 10-24 it was topped up with
  26 newer files (anomaly v2 outputs, polyp_recon logs, session history), leaving 0 differences.
- Cancelled job 338334 (`migsync`, set by an earlier session to run 10-26 12:00). It copied
  without `--update`, so after the switch it would have overwritten newer /nfs-stor files with the
  stale /l versions. The owner runs the final sync after the path change instead.
- Deleted the redundant `*.tar` archives on /nfs-stor (≈337 GB); the unpacked copies had been
  checked against the source.
- Owner decision: switch every path. `/l/users/` → `/nfs-stor/` in scripts, configs, docs and
  reports of HTA11, promoterVI, Therapeutic and spatial_variants, plus `~/.claude/CLAUDE.md`,
  `~/POLICY.md`, `k2` and the home symlinks. Not rewritten: session logs, file-history,
  `~/migration/migrate.sh`. Backup of the edited files is in this session's scratchpad.
- Conda envs and venvs on /nfs-stor have the old prefix baked in. Text files are rewritten; binary
  files cannot take the longer prefix, so each env gets an import test on a compute node.
- 10-25, done: (1) the queue was empty and a `-u` dry run showed 0 files missing on /nfs-stor;
  (2) reachability jobs 341954 (cn-10, cpu) and 341955 (gpu-52, gpu) could list, read, write
  64 MB and delete under /nfs-stor/yuqi.lei; (3) jobs 341957/341959 relinked 16 symlinks and
  rewrote 2,321 text files inside /nfs-stor (backups `/nfs-stor/yuqi.lei/.migration_rewrite_backup{,2}.tgz`).
  All 11 Python envs import from the new prefix. (4) The final `rsync -a -u` copied 0 files.
  The `faculty` partition used by some Therapeutic scripts does not exist on this cluster, so
  it was not tested.
- About 76k binary files in the envs still embed `/l/users`: almost all `.pyc` (only traceback
  names), plus about 200 conda `.so` and tools with built-in default paths (openssl, terminfo,
  tcl, Qt). Imports pass, but these fallbacks point at /l once it is gone (see KNOWLEDGE.md).
- 10-25, backup gaps: /nfs-stor is cluster storage like `$HOME`, so the migration is not a
  backup. Only GitHub or off-cluster copies survive a cluster loss. HTA11 env exported to `env/`
  (conda explicit + yml + pip layers, rebuild steps). Therapeutic is now a git repo pushed to
  github.com/CyclopsRay/Therapeutic (`009f78c`); its private docs, `repro/`, third-party clones
  and paper PDFs stay out by design.

## 2026-10-25 — Progress-report figures and filled TBDs

- All jobs had finished: anomaly v2 (341132/341133), flow 338315, Visium mapping 338316. No
  failures in the logs. `sacct` was down, so logs were the check.
- `scripts/make_report_figures.py` → `figures/report_fig1–5.png`, now in `draft_v1.md`. New
  panels: the three-step schematic (synthetic points), anomaly v2 new-cell AUROC with the
  depth-adjusted error (`recon_depth_adjusted.tsv`, detected genes), flow per person, and a Visium
  grid of 4 sections. fig22 (raw error) is not used.
- Fig 4 uses `ed_flow + growth`, the column behind the quoted 23/33, 25/33 and 0.17 vs 0.27. Plain
  `ed_flow` gives 24 and 26; the draft's Methods describes only the flow.
- Fig 5 shows the other-people reference giving *higher* purity on both serrated sections (AUC
  0.57 / 0.92 vs own 0.64 / 0.85 on 7663 / 6134). The "own cells find ASC that others miss" claim
  holds for the two adenomas only (7862, 10711).
- 10-25, owner request: Figure 1 is now the pipeline schematic. (a) VAE: healthy cells rebuilt as
  they went in, polyp cells rebuilt as healthy, so the error is large. (b) Unbalanced OT pairs
  (dot size = mass) plus the flow along a Y-shaped manifold. (c) Detailed spatial panel: crypts and
  polyp under the spot grid, one spot zoomed into ~10 cells, DestVI with the person's own cells,
  cell-type shares, purity map. The new-cell panel (fig8) moved to Fig 2a; the gene panels are now
  2b/2c, and the Results references were updated.
- **Correction (10-25)** to the Fig 5 note above. The other-people reference gives a higher
  *SSC level* on both serrated sections (adenoma-spot SSC 0.301 vs 0.233 on 7663; 0.364 vs 0.002 on
  6134). It gives a higher *AUC* only on 6134 (0.92 vs 0.85). On 7663 the person's own reference
  is better (0.64 vs 0.57). Overall the own reference has the higher AUC in 3 of 4 sections, as the
  10-23 report states.
- 10-25, owner decision: the progress report shows positive results only for now; models can be
  improved later. Negatives stay in the weekly report (10-23 sections and the anomaly v2 section).
  Figure layout is now: 1 pipeline; 2 data at a glance (label-free UMAP fig10, person highlight
  fig17, new cells fig8); 3 genes; 4 healthy-only model; 5 flow + the three Visium sections where
  the person's own reference beats the other (7862, 10711, 7663; 6134 dropped). The UMAPs had been
  left out of the 10-24 figure plan for space, not on purpose. Arms console republished (v15).
- 10-25: abstract opens with prevalence (GLOBOCAN 2022, Bray et al. 2024: 3rd most common, 2nd
  cancer death, ~1.9 M cases / ~900 k deaths). References renumbered by first appearance (now 16);
  all 15 DOIs checked against Crossref metadata, all match; Chen/Heiser e-page suffixes added.
  Figures: explanatory gray text removed at owner's request (captions carry it); panel titles
  shortened to Detect / Predict / Map. "33 patients" checked: 19 conventional + 15 serrated pairs,
  HTA11_6801 in both.
- 10-25: submission PDF `presentation/progress_report/progress_report.pdf` from
  `scripts/report_to_pdf.py` (fpdf2, STIX serif 11 pt, A4). 6 pages: text pp. 1–3, figures
  pp. 3–5, references p. 6 (references do not count toward the limit, owner). Fig 1 now has a and b
  side by side (3.5 in tall); Fig 5a shortened; Fig 5 is shrunk to fit page 5. Body ≈1,468 words.
  The internal provenance line under the figures was removed from the draft.
