#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v python >/dev/null 2>&1; then
  PYTHON="python"
else
  PYTHON="python3"
fi

if ! "$PYTHON" - <<'PY'
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("pytest") else 1)
PY
then
  echo "pytest is required. Run ./scripts/setup.sh to install dependencies." >&2
  exit 1
fi

PYTEST=("$PYTHON" -m pytest)
if "$PYTHON" - <<'PY'
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("xdist") else 1)
PY
then
  if ! "${PYTEST[@]}" -n auto; then
    echo "xdist run failed; retrying without xdist" >&2
    "${PYTEST[@]}"
  fi
else
  "${PYTEST[@]}"
fi
