#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$script_dir/.." && pwd)

# shellcheck source=common.sh
source "$script_dir/common.sh"

require_cmd node
require_cmd npm

log_step "Formatting and linting (Biome)"
(
  cd "$project_root"
  npx --no-install biome check --write .
)

log_step "Checking shell scripts"
(
  cd "$project_root"
  bash -n scripts/*.sh
)

if command -v shellcheck >/dev/null 2>&1; then
  log_step "Running shellcheck"
  (
    cd "$project_root"
    shellcheck scripts/*.sh
  )
else
  echo "shellcheck not installed; skipping."
fi

log_step "Running tests"
"$script_dir/test.sh"
