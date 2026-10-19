#!/usr/bin/env bash
# Download the OSF hftq2 files named in record/006_feasibility/osf_download_list.tsv
# (path, size, md5, url) and verify each md5. I/O only.
# Submit from the project root: sbatch scripts/download_osf_subset.sh
#SBATCH --job-name=hta11-osf-dl
#SBATCH --partition=cscc-cpu-p
#SBATCH --qos=cscc-cpu-qos
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00
#SBATCH --output=/l/users/yuqi.lei/HTA11/logs/osf_dl_%j.out
#SBATCH --error=/l/users/yuqi.lei/HTA11/logs/osf_dl_%j.err
set -euo pipefail
dest=/l/users/yuqi.lei/HTA11/data/osf_hftq2
while IFS=$'\t' read -r path size md5 url; do
  out="$dest$path"; mkdir -p "$(dirname "$out")"
  if [[ -f "$out" ]] && [[ $(md5sum "$out" | cut -d' ' -f1) == "$md5" ]]; then echo "ok (cached) $path"; continue; fi
  curl -sSL --retry 3 -o "$out.part" "$url"
  got=$(md5sum "$out.part" | cut -d' ' -f1)
  if [[ "$got" != "$md5" ]]; then echo "MD5 MISMATCH $path $got != $md5"; exit 1; fi
  mv "$out.part" "$out"; echo "ok $path $size"
done < /home/yuqi.lei/HTA11/record/006_feasibility/osf_download_list.tsv
