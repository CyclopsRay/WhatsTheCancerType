#!/usr/bin/env bash
# Paired polyp-vs-normal composition, PyDESeq2, route comparison, replication, GSEA.
# Submit from the project root: sbatch scripts/paired_analysis.sh
#SBATCH --job-name=hta11-paired
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=03:00:00
#SBATCH --output=/nfs-stor/yuqi.lei/HTA11/logs/paired_%j.out
#SBATCH --error=/nfs-stor/yuqi.lei/HTA11/logs/paired_%j.err

set -euo pipefail
/nfs-stor/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/paired_analysis.py \
  /nfs-stor/yuqi.lei/HTA11/derived/pseudobulk \
  /nfs-stor/yuqi.lei/HTA11/data/genesets/MSigDB_Hallmark_2020.gmt \
  /nfs-stor/yuqi.lei/HTA11/derived/paired \
  8
