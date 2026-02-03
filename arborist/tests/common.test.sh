#!/usr/bin/env bash
set -euo pipefail

test_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$test_dir/.." && pwd)

# shellcheck source=../scripts/common.sh
source "$project_root/scripts/common.sh"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

if ! log_step "Hello" | grep -q "==> Hello"; then
  fail "log_step output did not match"
fi

require_cmd bash

if (require_cmd "definitely_missing_cmd_123" 2>/dev/null); then
  fail "require_cmd should fail for missing command"
fi
