# Arborist Runner

Arborist is a CLI automation runner that coordinates Codex CLI across multiple
projects. It discovers projects with Arborist task files, runs Codex against
those projects with a fixed time budget, and loops continuously.

## Quick Start
1. `./scripts/setup.sh`
2. `./scripts/run_arborist.sh <projects-root>`

## Requirements
- Node.js (ESM-capable, Node 18+ recommended)
- npm
- `codex` CLI on PATH

## Key Scripts
- `scripts/run_arborist.sh`: launch the runner.
- `scripts/pre_commit.sh`: format, lint, and run fast tests.
- `scripts/test.sh`: run unit tests.

## Index
- `spec.md` — high-level plan and technical decisions.
- `code_review.md` — manual review checklist for changes.
- `docs/README.md` — project documentation hub.
