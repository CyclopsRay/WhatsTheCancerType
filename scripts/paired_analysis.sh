#!/usr/bin/env bash
# Paired polyp-vs-normal composition, PyDESeq2, route comparison, replication, GSEA.
# Submit from the project root: sbatch scripts/paired_analysis.sh
#SBATCH --job-name=hta11-paired
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=03:00:00
#SBATCH --output=/l/users/yuqi.lei/HTA11/logs/paired_%j.out
#SBATCH --error=/l/users/yuqi.lei/HTA11/logs/paired_%j.err

set -euo pipefail
/l/users/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/paired_analysis.py \
  /l/users/yuqi.lei/HTA11/derived/pseudobulk \
  /l/users/yuqi.lei/HTA11/data/genesets/MSigDB_Hallmark_2020.gmt \
  /l/users/yuqi.lei/HTA11/derived/paired \
  8
