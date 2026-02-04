# Arborist Project Specification

## Overview
Arborist is a CLI automation runner that coordinates Codex CLI across projects in a
folder. It discovers projects with Arborist task files, runs Codex against each
project with a fixed time budget, and keeps looping for continuous maintenance.

## Goals
- Provide predictable, repeatable execution of Codex tasks across multiple
  projects.
- Minimize manual coordination by automating discovery, prompting, and cleanup.
- Keep the runtime simple and portable (single Node.js entry point + shell wrapper).
- Ensure tasks and feedback are processed in a consistent, auditable way.

## High-Level Plan
1. Complete project setup (spec, tooling, scripts, docs, and tests).
2. Harden the core runner (`scripts/arborist.mjs`) for reliable looping behavior.
3. Add MVP work items for discovery, prompting, and cleanup workflows.
4. Expand documentation and operational guides as features land.

## Non-goals
- No GUI or web dashboard in the MVP.
- No replacement for human review; outputs are still reviewed in repo.
- No complex scheduling beyond the fixed time budget loop.

## Users
- Developers running Codex CLI to maintain multiple repositories/projects.

## Architecture
- `scripts/arborist.mjs` (Node.js ESM) discovers candidate projects, executes
  Codex runs, and manages list file cleanup.
- `scripts/run_arborist.sh` (Bash) ensures Node/npm availability, installs
  dependencies at repo root, then launches the Node entry point.
- Project indicators: `arborist/tasks.md`, `arborist/todo.md`, `arborist/feedback.md`, `SEED.md`.

## Data Flow
1. Discover projects with indicator files.
2. Read `arborist/todo.md`, `arborist/tasks.md`, and `arborist/feedback.md` to determine remaining work.
3. Spawn `codex exec` with the appropriate prompt for each project.
4. When all work is complete, clear list files to titles only.

## Technical Decisions
- Language: Node.js (ESM) to match existing scripts and provide reliable
  filesystem + process control.
- Shell: Bash for lightweight bootstrapping and environment checks.
- Formatting/Linting: Biome for fast, auto-fixing style and lint checks.
- Shell linting: `bash -n` for syntax plus `shellcheck` when available.
- Testing: Node's built-in test runner for fast unit tests.
- Type checking: Not required for MVP; the current surface area is small and
  ESM + lint rules provide sufficient safety. Revisit if the codebase grows.

## Testing Strategy
- Fast unit tests only (`node --test`) and kept under one second per test file.
- Lightweight Bash checks executed from `scripts/pre_commit.sh`.
- Integration tests deferred until a richer CLI interface exists.

## Operational Notes
- Avoid destructive file operations and prefer explicit list clearing.
- Keep logs minimal but actionable for troubleshooting.

## MVP Definition
- Run the Arborist loop against a directory of projects.
- Correctly handle missing indicator files and set up new projects.
- Provide reliable scripts for setup, lint/format, and tests.
