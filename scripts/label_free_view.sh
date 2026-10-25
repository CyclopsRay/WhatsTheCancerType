#!/usr/bin/env bash
# Label-free PCA/UMAP from raw counts (no labels, no batch correction) + one-person view.
# Submit from the project root: sbatch scripts/label_free_view.sh
#SBATCH --job-name=hta11-labelfree
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --time=01:30:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/labelfree_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/labelfree_%j.err

set -euo pipefail
D=/nfs-stor/yuqi.lei/HTA11
/nfs-stor/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/label_free_view.py \
  $D/data/vanderbilt_cellxgene $D/derived/pseudobulk $D/derived/label_free /home/yuqi.lei/HTA11/figures
