#!/usr/bin/env bash
# Quick hypothesis checks on the saved pseudobulk (X1–X5); see hypothesis_checks.py.
# Submit from the project root: sbatch scripts/hypothesis_checks.sh
#SBATCH --job-name=hta11-hypo
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/hypo_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/hypo_%j.err

set -euo pipefail
/nfs-stor/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/hypothesis_checks.py \
  /nfs-stor/yuqi.lei/HTA11/derived/pseudobulk \
  /nfs-stor/yuqi.lei/HTA11/derived/paired \
  /nfs-stor/yuqi.lei/HTA11/derived/hypothesis
