#!/usr/bin/env bash
# Step 4 pilot: same-person unbalanced OT between a donor's polyp and normal cells.
# Submit from the project root: sbatch scripts/cell_matching.sh [--test]
#SBATCH --job-name=hta11-ot
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=/l/users/yuqi.lei/HTA11/logs/ot_%j.out
#SBATCH --error=/l/users/yuqi.lei/HTA11/logs/ot_%j.err

set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
/l/users/yuqi.lei/venvs/hta11/bin/python /home/yuqi.lei/HTA11/scripts/cell_matching.py \
  /l/users/yuqi.lei/HTA11/data/vanderbilt_cellxgene \
  /l/users/yuqi.lei/HTA11/derived/pseudobulk \
  /l/users/yuqi.lei/HTA11/derived/cell_matching \
  16 "$@"
