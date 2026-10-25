#!/usr/bin/env bash
# Marker-gene polyp/normal calls on the 7 Visium polyp captures vs pathologist annotation.
# Submit from the project root: sbatch scripts/visium_marker_calls.sh
#SBATCH --job-name=hta11-vismark
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/vismark_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/vismark_%j.err

set -euo pipefail
D=/nfs-stor/yuqi.lei/HTA11
/nfs-stor/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/visium_marker_calls.py \
  $D/data/osf_hftq2/ST_master $D/derived/visium /home/yuqi.lei/HTA11/figures
