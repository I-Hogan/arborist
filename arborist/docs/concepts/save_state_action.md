# Save State Action Plan

## Goals
- Allow the web UI to trigger a "save state" action for the active project.
- Save state should create a commit with all current changes and push to `main`.
- When the active project is the Arborist project, commit at the workspace root.

## API Plan
- `POST /api/save-state`.
- Request body: empty.
- Response: `{ activeProject, result: { status, message, commitSha?, commitRoot } }`.
- Error conditions (400): no active project, not a git repo, not on `main`.
- No-op condition (200): no local changes to commit.

## Implementation Plan
- Resolve the active project.
- Compute the commit root: active project root unless it matches the Arborist project root, then use the workspace root.
- Verify git is available and the target is a git repo.
- Require the current branch to be `main`.
- Check for changes via `git status --porcelain`.
- If changes exist: `git add -A`, `git commit -m "Save state for <project> (<timestamp>)"`, `git push origin main`.

## UI Plan
- Enable the Save State button only when an active project is selected and the action is not busy.
- Show the target project name and a status line for progress/errors.
- Display clear responses for success, no-op, and failures.
