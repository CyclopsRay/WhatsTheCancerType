# Current status

Live board of every arm: [HTA11 Arms Console](https://claude.ai/artifact/EAd4sS1nSVmPepYoRBhZpF)
(source `console/index.html`, republish after each change).

## Deadlines

- **Midterm talk, 3–5 min:** Thu 2026-10-22. Deck (13 slides; slides 5+ simplified 2026-10-22: idea, first-test design, label-free
  look, person fingerprint + explorer, textbook agreement, single cell vs tissue, next steps, spatial plan): https://claude.ai/artifact/VVPjMSC6a5dnFAbnEYHG7G
- **Progress report, ≤1500 words, ≤5 figures:** Sat 2026-10-24. Each student writes
  their own text; numbers and figures from `report/10_23_report.md` and `figures/`.
  Draft v1 (owner revises by hand): `presentation/progress_report/draft_v1.md`; framing notes in
  [10_30_record.md](report/10_30_record.md).
- Instructors asked the team to meet one of them about feasibility.

## Just finished, still being analysed (2026-10-19)

- First end-to-end paired run (jobs 325071, 325099, 325107, 325109 — all completed).
  Composition, PyDESeq2 per route, shared-vs-specific split, DIS→VAL replication,
  Hallmark GSEA, Visium scoring. Results in [10_23_report.md](report/10_23_report.md);
  provenance in [record 006](record/006_feasibility/README.md).
- Open analysis items before the progress report:
  - Marker check of the published `Cell_Type` labels (slide says "next").
  - High mito fraction in DIS (median 37–44 % per specimen) — decide whether to filter.
  - Why 2/9 DIS serrated donors show ~0 SSC (not HP vs SSL: HP carries SSC too).
  - Pooled DIS+VAL fit (19 / 15 donors).

## Just finished, still being analysed (2026-10-20)

- Hypothesis checks X1–X6 (jobs 327343, 327354), results in the report's 10-20 section.
  X1/X4/X5 on slides; X2 negative (delta does not sharpen coarse route calls); X6 modest
  (pairing: more hits in 3/4 fits, ~16 % smaller SE, same replication).
- Open: HTA11_6801's TA scores as high on the serrated signature as its SSL — mixed lesion,
  donor field, or label issue?
- Step 4 first run done (jobs 327373 test, 327374 full): same-person unbalanced OT.
  ASC → own STM 11/14, SSC → own ABS 9/10, stable over 5 settings; positive control 0.81–0.94;
  lesion states least matched in 23/24. Slide 9 updated. Open: shuffled-label null and
  leave-one-donor-out for the matching; own-vs-other cost is weak (10/33).
- Marker check done: labels supported; stem markers peak in ASC, then STM.

## Just finished, still being analysed (2026-10-22)

- Label-free map (job 332524) and stem/mature gene scores (job 332647); results in the report's
  10-22 section, figures fig10–14, deck slides `look`, `person`, `newcells`, `genes`.
  Open: polyp cells cluster by person without correction (clonal outgrowth vs handling?);
  serrated no-look-alike cells lean on one person (52–58 %).

## Just finished, still being analysed (2026-10-23): the four next-step models

Jobs 338312–338316 all completed; results in the report's 10-23 sections, figs 18–21, design in the
record. Scripts `scripts/{person_free,polyp_anomaly,polyp_flow,visium_mapping}.{py,sh}` (GPU).
- Person-free scVI: healthy same-person share halved, ASC/SSC stay apart; still 4× chance.
- Anomaly (held out): median AUROC 0.66 / 0.73; SSC most anomalous, ASC not.
- Flow: negative vs "other people's polyps" baseline; open whether to rerun in the person-free latent.
- DestVI: route 6/7 with own cells; no spread signal (only 2 slices usable).
Open: owner to pick follow-ups (PLAN.md, "Four next-step models"); none submitted.

## Just finished, still being analysed (2026-10-24): anomaly v2 (jobs 341132, 341133)

Healthy-only VAE reconstruction error; results in [10_30_report.md](report/10_30_report.md).
Raw error is depth-driven (ρ −0.94); depth-adjusted from saved tables. Error finds ASC (0.78),
hidden-layer distance finds SSC (0.85). Open: build the depth calibration into the script
(simulated-count expected deviance) and redraw fig22; decide whether to mask ambient genes.

## Blocked / parked

- Synapse Level-4 objects (governance issue; no credentials on host).
- Genotype extension (needs the Synapse VCFs).

## Current reporting interval

Week ending 2026-10-30: [record](report/10_30_record.md), [results](report/10_30_report.md). Previous: [10_23 results](report/10_23_report.md).
Select again with `bash scripts/ensure_week.sh` before each weekly update.
Forward actions are in [PLAN.md](PLAN.md).
