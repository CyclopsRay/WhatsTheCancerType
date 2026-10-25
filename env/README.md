# HTA11 environment

All HTA11 scripts run `/nfs-stor/yuqi.lei/venvs/hta11/bin/python`. That venv is a thin layer
(`--system-site-packages`) on the conda env `/nfs-stor/yuqi.lei/envs/promotervi`
(Python 3.10, torch 2.1.2 + CUDA 11.8, scanpy 1.11.5, scvi-tools 1.3.3). The PDF helper
`scripts/md_to_pdf.py` uses a separate venv, `hta11-doc`, on the system Python 3.12.

Exported 2026-10-25, linux-64.

| File | Layer |
|---|---|
| `promotervi_conda_explicit.txt` | conda base, exact package URLs and builds (preferred for rebuild) |
| `promotervi_conda.yml` | the same base as name=version=build, channel list included |
| `promotervi_pip_all.txt` | everything Python sees in the base, including pip-only packages |
| `hta11_venv_extra.txt` | what the `hta11` venv adds (pydeseq2, gseapy, ...) |
| `hta11_doc_requirements.txt` | the `hta11-doc` venv (fpdf2, pypdf) |

## Rebuild

```bash
B=/nfs-stor/$USER        # or wherever large files now live
MM=$B/bin/micromamba     # any micromamba/conda works
$MM create -y -p $B/envs/promotervi -f promotervi_conda_explicit.txt
$B/envs/promotervi/bin/python -m pip install -r promotervi_pip_all.txt   # adds pip-only packages
$B/envs/promotervi/bin/python -m venv --system-site-packages $B/venvs/hta11
$B/venvs/hta11/bin/pip install -r hta11_venv_extra.txt
python3.12 -m venv $B/venvs/hta11-doc && $B/venvs/hta11-doc/bin/pip install -r hta11_doc_requirements.txt
```

If the base path changes, replace `/nfs-stor/yuqi.lei/venvs/hta11` in `scripts/*.sh`. Run the
build through Slurm, not on the login node. The `promotervi` env is shared with the promoterVI
project; re-export these files after installing anything into it.
