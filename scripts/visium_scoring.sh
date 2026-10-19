#!/usr/bin/env bash
# Score DIS-derived signatures on the 7 OSF Visium polyp captures.
# Submit from the project root after paired_analysis: sbatch scripts/visium_scoring.sh
#SBATCH --job-name=hta11-visium
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/l/users/yuqi.lei/HTA11/logs/visium_%j.out
#SBATCH --error=/l/users/yuqi.lei/HTA11/logs/visium_%j.err
set -euo pipefail
/l/users/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/visium_scoring.py \
  /l/users/yuqi.lei/HTA11/data/osf_hftq2/ST_master \
  /l/users/yuqi.lei/HTA11/derived/paired \
  /l/users/yuqi.lei/HTA11/derived/visium
