#!/usr/bin/env bash
# Select the current reporting interval at write time; never infer from filenames.
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 /home/yuqi.lei/.local/bin/research-week --project "$project_dir" --ensure
