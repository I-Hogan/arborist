# How to run Arborist on a workspace

This guide covers the required files, recommended folder structure, and
expected behavior when you run Arborist against a workspace directory.

## Prerequisites
- Node.js (ESM-capable; Node 18+ recommended)
- npm
- `codex` CLI on PATH

## Required files
Arborist discovers projects by looking for any of these indicator files in the
workspace root or in an immediate subdirectory:
- `tasks.md`
- `todo.md`
- `SEED.md`
- `feedback.md`
- `user_requests.md`

To actually process a project, `tasks.md` and `todo.md` must exist. If they are
missing, Arborist will invoke the project setup instructions to create them.

## Recommended folder structure
Keep projects as direct children of the workspace root so Arborist can find
indicator files quickly.

Example:

```
workspace/
  arborist/              # the Arborist runner repo (this project)
  project-alpha/
    AGENTS.md
    SEED.md
    tasks.md
    todo.md
    feedback.md
    backlog.md
    docs/
    experiments/
    scripts/
  project-beta/
    AGENTS.md
    SEED.md
    tasks.md
    todo.md
    feedback.md
    backlog.md
    docs/
    experiments/
    scripts/
```

For new projects, copy the templates from `templates/arborist`, `templates/docs`,
`templates/experiments`, and `templates/scripts` into the project directory to
get the standard Arborist layout.

## Run Arborist
From the Arborist repo:

```
./scripts/run_arborist.sh <projects-root>
```

If you omit `<projects-root>`, Arborist uses the repo root as the workspace
folder.

## Expected behavior
- Scans the workspace root and its immediate subdirectories (excluding hidden
  folders and `node_modules`) for indicator files.
- For each discovered project, runs Codex with the prompt to complete the next
  `todo.md` item and follow the `complete_next_item.md` instructions.
- Uses a fixed 4-hour time budget per project run; stops before starting a new
  task if the budget is exhausted.
- If `tasks.md` or `todo.md` are missing, runs the project setup instructions
  from `project_setup.md`.
- When `todo.md`, `tasks.md`, and `feedback.md` have no remaining items and no
  timeouts occurred, clears list files back to their headers.
- Waits 60 seconds between workspace passes and repeats the loop.
