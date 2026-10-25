#!/usr/bin/env bash
# Score DIS-derived signatures on the 7 OSF Visium polyp captures.
# Submit from the project root after paired_analysis: sbatch scripts/visium_scoring.sh
#SBATCH --job-name=hta11-visium
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/visium_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/visium_%j.err
set -euo pipefail
/nfs-stor/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/visium_scoring.py \
  /nfs-stor/yuqi.lei/HTA11/data/osf_hftq2/ST_master \
  /nfs-stor/yuqi.lei/HTA11/derived/paired \
  /nfs-stor/yuqi.lei/HTA11/derived/visium
