#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if command -v python >/dev/null 2>&1; then
  PYTHON="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  echo "Python 3 is required to run this project." >&2
  exit 1
fi

if [ ! -d ".venv" ]; then
  "$PYTHON" -m venv .venv
fi

VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
if [ ! -x "$VENV_PYTHON" ]; then
  VENV_PYTHON="$ROOT_DIR/.venv/Scripts/python.exe"
fi
if [ -x "$VENV_PYTHON" ]; then
  PYTHON="$VENV_PYTHON"
fi

"$PYTHON" -m pip install --upgrade pip

if [ -f "requirements.txt" ]; then
  "$PYTHON" -m pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
  "$PYTHON" -m pip install -r requirements-dev.txt
else
  "$PYTHON" -m pip install ruff pytest pytest-xdist
fi

echo "Setup complete."
