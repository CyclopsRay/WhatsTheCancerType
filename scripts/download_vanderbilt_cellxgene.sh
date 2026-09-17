#!/usr/bin/env bash
# Download the public, processed Vanderbilt Chen et al. (2021) CELLxGENE objects.
# Submit with: sbatch scripts/download_vanderbilt_cellxgene.sh
# Destination is persistent cluster storage, never the home/project directory.
# This is I/O only; it does not run any analysis.
#SBATCH --job-name=hta11-vumc-rna-download
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=04:00:00
#SBATCH --output=/l/users/yuqi.lei/HTA11/logs/vanderbilt_download_%j.out
#SBATCH --error=/l/users/yuqi.lei/HTA11/logs/vanderbilt_download_%j.err

set -euo pipefail

dest_dir=/l/users/yuqi.lei/HTA11/data/vanderbilt_cellxgene
mkdir -p "$dest_dir"

download() {
  local url=$1
  local filename=$2
  local expected_bytes=$3
  local partial_path="$dest_dir/$filename.part"
  local final_path="$dest_dir/$filename"

  if [[ -f "$final_path" ]] && [[ $(stat -c '%s' "$final_path") -eq "$expected_bytes" ]]; then
    echo "Already complete: $final_path"
    return
  fi

  if [[ -f "$partial_path" ]]; then
    curl --fail --location --retry 5 --retry-all-errors --continue-at - \
      --output "$partial_path" "$url"
  else
    curl --fail --location --retry 5 --retry-all-errors \
      --output "$partial_path" "$url"
  fi
  [[ $(stat -c '%s' "$partial_path") -eq "$expected_bytes" ]]
  mv "$partial_path" "$final_path"
  sha256sum "$final_path"
}

download \
  'https://datasets.cellxgene.cziscience.com/9da034b0-de48-47ab-97f6-21b5f2dbd1a4.h5ad' \
  'vanderbilt_dis_epithelial.h5ad' 1524773102
download \
  'https://datasets.cellxgene.cziscience.com/6f8f0b95-3779-4c0e-824d-4810c39f008c.h5ad' \
  'vanderbilt_val_epithelial.h5ad' 1145423183
download \
  'https://datasets.cellxgene.cziscience.com/91a55470-7520-4ecf-bcbc-1062f7ef4cdb.h5ad' \
  'vanderbilt_dis_val_non_epithelial.h5ad' 144074797
