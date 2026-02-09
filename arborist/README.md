# Arborist Runner

Arborist is a CLI automation runner that coordinates Codex CLI across multiple
projects. It discovers projects with Arborist task files, runs Codex against
those projects with a fixed time budget, and loops continuously.

## Quick Start
1. `./scripts/setup.sh`
2. `./scripts/run_workspace.sh <projects-root>`

## Requirements
- Node.js (ESM-capable, Node 18+ recommended)
- npm
- `codex` CLI on PATH
- Optional: `pre-commit` for safety hooks

## Key Scripts
- `scripts/run_workspace.sh`: launch the runner and local website together.
- `scripts/run_arborist.sh`: launch the runner.
- `scripts/web_ui.mjs`: launch the local web UI shell on port 7788.
- `scripts/pre_commit.sh`: format, lint, and run fast tests.

## Web UI
`./scripts/run_workspace.sh` prints the website URL (default:
`http://localhost:7788`) when it starts.

You can still start the local UI shell separately with either of the following commands:
- `node scripts/web_ui.mjs`
- `npm run ui`
The UI binds to localhost only. Set `ARBORIST_UI_PORT` to override the default port (7788).
The UI is built with Astro; run `npm run ui:build` after editing `web_ui/src` or
`web_ui/public` to regenerate the static output.

## Safety Hooks
If you have `pre-commit` installed, run `pre-commit install` to enable safety
checks (merge conflict markers, secrets, large files, symlinks, and config
validation). To run them manually, use `pre-commit run --all-files`.

## Index
- `arborist/spec.md` — high-level plan and technical decisions.
- `code_review.md` — manual review checklist for changes.
- `docs/README.md` — project documentation hub.
