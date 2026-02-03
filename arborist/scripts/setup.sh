#!/usr/bin/env bash
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$script_dir/.." && pwd)

# shellcheck source=common.sh
source "$script_dir/common.sh"

require_cmd node
require_cmd npm

log_step "Installing npm dependencies"
(
  cd "$project_root"
  npm install
)
