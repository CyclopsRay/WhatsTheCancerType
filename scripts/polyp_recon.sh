#!/usr/bin/env bash
# Anomaly v2: healthy-only VAE, reconstruction error + hidden-layer distance. Arg: hvg | detected.
# Submit from the project root: sbatch scripts/polyp_recon.sh {hvg,detected} [--test]
#SBATCH --job-name=hta11-recon
#SBATCH --partition=cscc-gpu-p
#SBATCH --qos=cscc-gpu-qos
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=/l/users/yuqi.lei/HTA11/logs/polyp_recon_%j.out
#SBATCH --error=/l/users/yuqi.lei/HTA11/logs/polyp_recon_%j.err

set -euo pipefail
[ -d /l/users/yuqi.lei/HTA11/data ] || { echo "/l not mounted on $(hostname); resubmit with --exclude"; exit 1; }
cd /home/yuqi.lei/HTA11/scripts
D=/l/users/yuqi.lei/HTA11
/l/users/yuqi.lei/venvs/hta11/bin/python polyp_recon.py \
  $D/data/vanderbilt_cellxgene $D/derived/pseudobulk $D/derived/anomaly /home/yuqi.lei/HTA11/figures "$@"
