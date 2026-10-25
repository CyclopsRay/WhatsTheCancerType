#!/usr/bin/env bash
# Next step 4: DestVI unmixing of the 7 Visium polyp captures, same-person vs other-people reference.
# Submit from the project root: sbatch scripts/visium_mapping.sh [--test]
#SBATCH --job-name=hta11-vmap
#SBATCH --partition=cscc-gpu-p
#SBATCH --qos=cscc-gpu-qos
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/visium_mapping_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/visium_mapping_%j.err

set -euo pipefail
[ -d /nfs-stor/yuqi.lei/HTA11/data ] || { echo "/l not mounted on $(hostname); resubmit with --exclude"; exit 1; }
cd /home/yuqi.lei/HTA11/scripts
D=/nfs-stor/yuqi.lei/HTA11
/nfs-stor/yuqi.lei/venvs/hta11/bin/python visium_mapping.py \
  $D/data/vanderbilt_cellxgene $D/derived/pseudobulk $D/data/osf_hftq2/ST_master $D/derived/visium $D/derived/visium_mapping /home/yuqi.lei/HTA11/figures "$@"
