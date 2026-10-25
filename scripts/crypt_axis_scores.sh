#!/usr/bin/env bash
# Stem and mature-absorptive marker scores per cell (crypt axis), per-person medians.
# Submit from the project root: sbatch scripts/crypt_axis_scores.sh
#SBATCH --job-name=hta11-crypt
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=2
#SBATCH --mem=24G
#SBATCH --time=00:30:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/crypt_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/crypt_%j.err

set -euo pipefail
D=/nfs-stor/yuqi.lei/HTA11
/nfs-stor/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/crypt_axis_scores.py \
  $D/data/vanderbilt_cellxgene $D/derived/pseudobulk $D/derived/label_free
