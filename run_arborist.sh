#!/usr/bin/env bash
set -euo pipefail

echo "Launching arborist..."

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required to run arborist.mjs." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to install dependencies." >&2
  exit 1
fi

if [ ! -f "$script_dir/package.json" ]; then
  cat <<'JSON' > "$script_dir/package.json"
{
  "name": "arborist",
  "private": true,
  "type": "module",
  "dependencies": {
    "@openai/codex-sdk": "*"
  }
}
JSON
fi

if [ ! -d "$script_dir/node_modules" ]; then
  npm install --silent
fi

exec node "$script_dir/arborist.mjs" "$@"
