#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$script_dir/.." && pwd)
repo_root="$project_root"

# shellcheck source=common.sh
source "$script_dir/common.sh"

require_cmd node
require_cmd npm

if command -v git >/dev/null 2>&1; then
  repo_root=$(git -C "$project_root" rev-parse --show-toplevel 2>/dev/null || echo "$project_root")
fi

log_step "Installing npm dependencies"
(
  cd "$project_root"
  npm install
)

if command -v pre-commit >/dev/null 2>&1; then
  config_path="$repo_root/.pre-commit-config.yaml"
  if [[ ! -f "$config_path" ]]; then
    config_path="$project_root/.pre-commit-config.yaml"
  fi
  log_step "Installing pre-commit hook"
  (
    cd "$repo_root"
    pre-commit install --config "$config_path"
  )
else
  echo "pre-commit not installed; skipping hook install."
fi
