#!/usr/bin/env bash
# X6: paired (~donor + condition) vs unpaired (~condition) DESeq2; see pairing_benefit.py.
# Submit from the project root: sbatch scripts/pairing_benefit.sh
#SBATCH --job-name=hta11-x6
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=/l/users/yuqi.lei/HTA11/logs/x6_%j.out
#SBATCH --error=/l/users/yuqi.lei/HTA11/logs/x6_%j.err

set -euo pipefail
/l/users/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/pairing_benefit.py \
  /l/users/yuqi.lei/HTA11/derived/pseudobulk \
  /l/users/yuqi.lei/HTA11/derived/hypothesis \
  8
