#!/usr/bin/env bash
# Next step 3: healthy-to-polyp flow (OT pairs + flow matching + growth), leave-one-person-out.
# Submit from the project root: sbatch scripts/polyp_flow.sh [--test]
#SBATCH --job-name=hta11-flow
#SBATCH --partition=cscc-gpu-p
#SBATCH --qos=cscc-gpu-qos
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=06:00:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/polyp_flow_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/polyp_flow_%j.err

set -euo pipefail
[ -d /nfs-stor/yuqi.lei/HTA11/data ] || { echo "/l not mounted on $(hostname); resubmit with --exclude"; exit 1; }
cd /home/yuqi.lei/HTA11/scripts
D=/nfs-stor/yuqi.lei/HTA11
/nfs-stor/yuqi.lei/venvs/hta11/bin/python polyp_flow.py \
  $D/data/vanderbilt_cellxgene $D/derived/pseudobulk $D/derived/flow /home/yuqi.lei/HTA11/figures "$@"
