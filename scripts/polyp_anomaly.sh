#!/usr/bin/env bash
# Next step 2: leave-one-person-out anomaly score (healthy-only scVI and PCA).
# Submit from the project root: sbatch scripts/polyp_anomaly.sh [--test]
#SBATCH --job-name=hta11-anom
#SBATCH --partition=cscc-gpu-p
#SBATCH --qos=cscc-gpu-qos
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=10:00:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/polyp_anomaly_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/polyp_anomaly_%j.err

set -euo pipefail
[ -d /nfs-stor/yuqi.lei/HTA11/data ] || { echo "/l not mounted on $(hostname); resubmit with --exclude"; exit 1; }
cd /home/yuqi.lei/HTA11/scripts
D=/nfs-stor/yuqi.lei/HTA11
/nfs-stor/yuqi.lei/venvs/hta11/bin/python polyp_anomaly.py \
  $D/data/vanderbilt_cellxgene $D/derived/pseudobulk $D/derived/label_free $D/derived/anomaly /home/yuqi.lei/HTA11/figures "$@"
