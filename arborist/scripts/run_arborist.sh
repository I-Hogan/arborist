#!/usr/bin/env bash
set -euo pipefail

echo "Launching arborist..."

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$script_dir/../.." && pwd)

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required to run arborist.mjs." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to install dependencies." >&2
  exit 1
fi

if [ ! -f "$project_root/package.json" ]; then
  cat <<'JSON' > "$project_root/package.json"
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

if [ ! -d "$project_root/node_modules" ]; then
  npm --prefix "$project_root" install --silent
fi

if [ "$#" -eq 0 ]; then
  exec node "$script_dir/arborist.mjs" "$project_root"
fi

exec node "$script_dir/arborist.mjs" "$@"
