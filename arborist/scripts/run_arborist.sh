#!/usr/bin/env bash
set -euo pipefail

echo "Launching arborist..."

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
project_root=$(cd "$script_dir/../.." && pwd)

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required to run arborist.mjs." >&2
  exit 1
fi

npm_available=true
if ! command -v npm >/dev/null 2>&1; then
  echo "Warning: npm not found; skipping dependency installs." >&2
  npm_available=false
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

if $npm_available && [ ! -d "$project_root/node_modules" ]; then
  if node -e 'const fs=require("fs");const pkg=JSON.parse(fs.readFileSync(process.argv[1],"utf8"));const depCount=Object.keys(pkg.dependencies||{}).length+Object.keys(pkg.devDependencies||{}).length;process.exit(depCount>0?0:1);' \
    "$project_root/package.json"; then
    if ! npm --prefix "$project_root" install --silent; then
      echo "Warning: unable to install workspace dependencies; continuing." >&2
    fi
  else
    echo "Skipping workspace npm install (no dependencies)." >&2
  fi
fi

if [ "$#" -eq 0 ]; then
  node "$script_dir/arborist.mjs" "$project_root"
else
  node "$script_dir/arborist.mjs" "$@"
fi
