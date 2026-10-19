# Current status

Live board of every arm: [HTA11 Arms Console](https://claude.ai/artifact/EAd4sS1nSVmPepYoRBhZpF)
(source `console/index.html`, republish after each change).

## Deadlines

- **Midterm talk, 3–5 min:** Tue 2026-10-20 or Thu 2026-10-22 (sign up via the form
  in the instructors' email). Deck: https://claude.ai/artifact/VVPjMSC6a5dnFAbnEYHG7G
- **Progress report, ≤1500 words, ≤5 figures:** Sat 2026-10-24. Each student writes
  their own text; numbers and figures from `report/10_23_report.md` and `figures/`.
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

## Blocked / parked

- Synapse Level-4 objects (governance issue; no credentials on host).
- Genotype extension (needs the Synapse VCFs).

## Current reporting interval

Week ending 2026-10-23: [record](report/10_23_record.md), [results](report/10_23_report.md).
Select again with `bash scripts/ensure_week.sh` before each weekly update.
Forward actions are in [PLAN.md](PLAN.md).
