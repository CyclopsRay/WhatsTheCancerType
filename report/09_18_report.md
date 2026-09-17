# HTA11 — Weekly Report, week ending Friday 2026-09-18

Reporting interval: [2026-09-11T18:00:00+04:00, 2026-09-18T18:00:00+04:00) — Asia/Dubai.

Measured results only, with provenance; include positive and negative findings.

## 2026-09-17 — initialization result

- The project contains a documented scaffold (`CLAUDE.md`, `ONGOING.md`,
  `KNOWLEDGE.md`, and `PLAN.md`) and current-week report pair. Provenance:
  filesystem inspection of `/home/yuqi.lei/HTA11` before initialization.

## 2026-09-17 — Supplementary Table 4 metadata audit

Source: [Islam et al., Supplementary Table 4](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-024-07954-4/MediaObjects/41586_2024_7954_MOESM6_ESM.xlsx).
Output: [`table4_audit.json`](../record/001_temporal_recording/table4_audit.json).
Reproduce with `python3 scripts/audit_table4.py`; this recounts supplied metadata,
not raw sequencing reads or independently inferred clonality.

| Measurement | Observed value | Worksheet / field |
|---|---:|---|
| Profiled polyp cohort | 116 rows | HTAN_Vanderbilt |
| Adenoma / serrated / unstated | 70 / 42 / 4 | HTAN_Vanderbilt / Sample_type |
| Distinct participant IDs in cohort sheet | 95 | HTAN_Vanderbilt / HTAN_ID |
| Human WES specimens | 96 (63 AD, 33 SER) | WES_human_polyps |
| Human WES with at least 3 APC mutations | 14/96 (14.58%) | WES_human_polyps / APC_mut_count |
| TCPS with at least 3 APC mutations | 57/300 (19.00%) | TCPS_Human_APC_count / #APC_mut |
| Mouse WES with at least 3 Apc mutations | 5/13 (38.46%) | Mouse_tumor_analysis / first table |
| scRNA analysis rows / distinct specimen IDs | 121 / 114 | scRNAseq_human_polyps / HTAN_SPECID |
| scRNA rows with numeric median VAF | 86 | scRNAseq_human_polyps / Median_VAF |

The source article reports 418 polyps overall and 96 patients in the profiled
cohorts; these totals are not fully reconciled by this workbook audit. See the
[weekly record](09_18_record.md) for follow-up decisions. The source workbook
SHA-256 and audit timestamp are stored with the output above.
