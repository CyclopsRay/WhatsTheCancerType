# 001 — Temporal recording of mammalian development and precancer

Islam et al., Nature 634, 1187–1195 (2024). DOI: 10.1038/s41586-024-07954-4.
Reviewed 2026-09-17. This is a literature review and supplementary-table audit.

## Biological question and disease

Can cell ancestry and division history explain development and the origin of
precancer? The disease focus is **colorectal precancer: conventional adenomas and
serrated polyps**. The central claim is that some lesions originate from multiple
normal founders. Mouse experiments supply engineered lineage records; human
tissue supplies endogenous mutations. The authors estimate 15–30% polyclonal
initiation, depending on the analysis. See [main paper, Fig. 4](https://www.nature.com/articles/s41586-024-07954-4#Fig4).

## Experiment map

| System | Experiment | Purpose / location |
|---|---|---|
| Mouse embryos | MARC1 × Cas9 barcoding; NSC–seq at E7.75, E8.5 and E9.5; E14.5 gut follow-up | Reconstruct developmental ancestry and division history; Figs. 1–3 |
| Mouse adult intestine | Single-cell transcriptomes, barcodes, tissue imaging | Trace epithelial progenitors; Fig. 3 / Extended Data 11 |
| Mouse intestinal adenomas | ApcMin/+ lineage analysis and tumour/normal WES | Test multiple founders; Fig. 4 / Extended Data 12 |
| Human polyps | scRNA-seq, paired WES, targeted DNA sequencing | Infer clonality in sporadic colorectal precancer; Fig. 4 |
| Published human CRC | Multiregion WES reanalysis, 23 specimens | Comparison with invasive cancer; Fig. 4f |

These are separate experimental arms, not longitudinal observation of the same
human polyps progressing to cancer. Breast-tumour spatial data appear as an
external method-validation example (Extended Data 3), not the main disease cohort.

## What the assays actually measure

[Supplementary Methods](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-024-07954-4/MediaObjects/41586_2024_7954_MOESM1_ESM.docx)
describe NSC–seq as modified inDrops capture of both mRNA and guide RNA. Self-mutating
guide sequences record ancestry; mitochondrial variants supplement lineage
information. Cell-line and mouse intestinal organoid experiments test barcode
recovery and timing. HEK293FT is a human cell-line platform test, while EpH4 is a
mouse mammary epithelial capture-efficiency test. Neither defines the clinical
cancer cohort. Imaging includes HCR RNA–FISH and immunofluorescence.

Human samples came from colonoscopy, with histopathology and blood-derived normal
DNA. Single-cell libraries used inDrops/TruDrop. Human WES used paired tumour/normal
variant calling; the TCPS panel targeted approximately 500× depth. SComatic and
Monopogen called variants from scRNA-seq reads. Analyses combined APC-mutation
counts, allele-frequency distributions, female X-inactivation mosaicism, and
selection models. Patients were not CRISPR-barcoded. Multiomics here does not mean
every cell received simultaneous RNA, DNA and chromatin assays.

## Verified inventory and unresolved denominators

See [table4_audit.json](table4_audit.json) and the
[weekly results](../../report/09_18_report.md) for reproducible counts from
[Supplementary Table 4](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41586-024-07954-4/MediaObjects/41586_2024_7954_MOESM6_ESM.xlsx).

- Cohort sheet: 116 rows (70 AD, 42 SER, 4 unstated); WES sheet: 96 (63 AD, 33 SER).
- At least three APC mutations: 14/96 human WES, 57/300 TCPS, 5/13 mouse WES.
- The scRNA analysis sheet has 121 rows, 114 distinct specimen IDs, and 86 numeric
  median-VAF entries. Rows, libraries, specimens, and participants are different units.
- The article's headline 418 polyps is not reconciled by simply adding the 96 WES
  and 300 targeted samples. The cohort sheet also contains 95 distinct HTAN_ID
  values, versus 96 patients reported in the text. Preserve both observations;
  establish a specimen-level join before using a combined denominator.

## Reproduce this inspection

From `/home/yuqi.lei/HTA11`:

```bash
python3 scripts/fetch_paper_sources.py
python3 scripts/fetch_paper_sources.py --download
python3 scripts/inspect_paper_supplements.py record/001_temporal_recording/sources/methods.docx
python3 scripts/inspect_paper_supplements.py record/001_temporal_recording/sources/table4.xlsx --rows 0
python3 scripts/audit_table4.py
bash scripts/ensure_week.sh
```

Requires Python 3 standard library, curl, and the host's research-week helper.
Downloads are small public supplements, validated as Office archives; existing
files are preserved. `sources/` is a regenerable download cache excluded from git.
Audit JSON records the source SHA-256. Generic sheet row counts include headings;
use the dedicated audit for the multi-table mouse sheet.

## Data and code entry points

- [Mouse GEO accession GSE235119](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE235119)
  — accession reported by the article; GEO inventory not yet verified.
- [HTAN portal](https://data.humantumoratlas.org/) — Vanderbilt atlas;
  article lists dbGaP phs002371. Access requirements and file inventory remain to be checked.
- [Author code](https://github.com/Ken-Lau-Lab/NSC-seq) — repository separates barcode
  processing, single-cell processing and tree reconstruction. Its README states
  that the CRISPR perturbation-screen application is a companion manuscript.

Next: map assay availability to unique specimens before choosing an analysis.
An expression matrix alone cannot reproduce read-level somatic variant calling.
No sequencing pipeline or Slurm job has been run.
