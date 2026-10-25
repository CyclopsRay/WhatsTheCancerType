#!/usr/bin/env bash
# Pseudobulk + composition + QC tables from the two epithelial H5ADs.
# Submit from the project root: sbatch scripts/build_pseudobulk.sh
#SBATCH --job-name=hta11-pseudobulk
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=2
#SBATCH --mem=24G
#SBATCH --time=01:00:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/pseudobulk_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/pseudobulk_%j.err

set -euo pipefail
/nfs-stor/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/build_pseudobulk.py \
  /nfs-stor/yuqi.lei/HTA11/data/vanderbilt_cellxgene \
  /nfs-stor/yuqi.lei/HTA11/derived/pseudobulk
