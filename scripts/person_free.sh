#!/usr/bin/env bash
# Next step 1: person-free scVI vs uncorrected PCA, kNN mixing and route-separation checks.
# Submit from the project root: sbatch scripts/person_free.sh [--test]
#SBATCH --job-name=hta11-pfree
#SBATCH --partition=cscc-gpu-p
#SBATCH --qos=cscc-gpu-qos
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/person_free_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/person_free_%j.err

set -euo pipefail
[ -d /nfs-stor/yuqi.lei/HTA11/data ] || { echo "/l not mounted on $(hostname); resubmit with --exclude"; exit 1; }
cd /home/yuqi.lei/HTA11/scripts
D=/nfs-stor/yuqi.lei/HTA11
/nfs-stor/yuqi.lei/venvs/hta11/bin/python person_free.py \
  $D/data/vanderbilt_cellxgene $D/derived/pseudobulk $D/derived/person_free /home/yuqi.lei/HTA11/figures "$@"
