# 006 — Feasibility run: the core analysis on the real data (2026-10-19)

Prompted by instructor feedback that the roadmap might need novel methods. This
record holds the provenance for the first end-to-end run; results are in
[report/10_23_report.md](../../report/10_23_report.md), reasoning in
[report/10_23_record.md](../../report/10_23_record.md).

## Files here

- `osf_hftq2_inventory.tsv` — every entry of OSF `hftq2` with size and md5, from
  `scripts/osf_inventory.py`. The 16 `MxIF/quantification` CSVs have the empty-file
  md5 `d41d8cd98f00b204e9800998ecf8427e`.
- `osf_download_list.tsv` — the 11 OSF files fetched by `scripts/download_osf_subset.sh`
  (7 Visium polyp captures, NMF spectra, `abnormal_epithelium.h5ad`, WES MAF + clinical).

## Pipeline (all via Slurm, env `/nfs-stor/yuqi.lei/venvs/hta11`)

| Step | Script | Output under `/nfs-stor/yuqi.lei/HTA11/` |
|---|---|---|
| Pseudobulk, composition, cell QC | `scripts/build_pseudobulk.sh` | `derived/pseudobulk/` |
| OSF subset download, md5 checked | `scripts/download_osf_subset.sh` | `data/osf_hftq2/` |
| Paired composition, PyDESeq2, route split, GSEA, donor consistency | `scripts/paired_analysis.sh` | `derived/paired/` |
| Replication only, from saved tables | `python scripts/paired_analysis.py --replicate derived/paired` | `derived/paired/replication_summary.tsv` |
| Visium signature scoring | `scripts/visium_scoring.sh` | `derived/visium/` |
| Figures | `python scripts/make_figures.py /nfs-stor/yuqi.lei/HTA11/derived figures` | `figures/` (in git) |
