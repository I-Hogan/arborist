#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v ruff >/dev/null 2>&1; then
  RUFF="ruff"
else
  if command -v python >/dev/null 2>&1; then
    PYTHON="python"
  else
    PYTHON="python3"
  fi
  RUFF="$PYTHON -m ruff"
fi

if $RUFF --version >/dev/null 2>&1; then
  $RUFF format .
else
  echo "ruff not available; skipping formatting step" >&2
fi
"$ROOT_DIR/scripts/style.sh"
"$ROOT_DIR/scripts/test.sh"
