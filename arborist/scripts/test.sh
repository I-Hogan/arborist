#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$script_dir/.." && pwd)

# shellcheck source=common.sh
source "$script_dir/common.sh"

require_cmd node

log_step "Running unit tests"
(
  cd "$project_root"
  pids=()
  node --test & pids+=("$!")
  if [[ -f tests/common.test.sh ]]; then
    bash tests/common.test.sh & pids+=("$!")
  fi
  for pid in "${pids[@]}"; do
    wait "$pid"
  done
)
