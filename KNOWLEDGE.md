# Project knowledge

## Durable facts

- The project directory was empty when initialized on 2026-09-17.
- The source study is Islam et al. (2024), DOI 10.1038/s41586-024-07954-4.
  Its main disease is colorectal precancer; mouse engineered lineage tracing and
  human endogenous-variant inference are distinct assay arms.
- Sample counts have different units and subsets. Do not interpret the headline
  418 polyps as 418 matched single-cell/exome specimens. See the first
  [research record](record/001_temporal_recording/README.md) for the audit and open discrepancies.
- Supplementary Table 4 contains multiple tables in the mouse sheet; counting
  every populated row as a tumour overcounts specimens. Use `scripts/audit_table4.py`.
- `rg` is unavailable on this host; use `find` and `grep` as fallbacks.
- GitHub repository: `CyclopsRay/WhatsTheCancerType`, local default branch `main`.
  Existing host SSH authentication can access it; HTTPS Git access had no usable
  credentials during setup. Use the SSH `origin` for host-side fetch/push.
- The initial read-only `.git` seen inside the sandbox was a placeholder: an
  approved host-side check found no actual directory. Approved `git init` created
  normal metadata without replacing an existing repository.
