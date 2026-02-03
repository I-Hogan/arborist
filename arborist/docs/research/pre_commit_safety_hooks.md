# Pre-commit Safety Hooks Research

## Context
We need a pre-commit hook setup that blocks risky commits when AI-generated
changes are pushed to public repositories. The requested checks include
conflict markers, secrets, large files, symlinks, and config validation.

## Options Considered
- `pre-commit` with `pre-commit-hooks` and `gitleaks` hooks
  - Pros: well-maintained hook set for merge conflicts/config validation; gitleaks
    provides robust secret scanning.
  - Cons: requires `pre-commit` to be installed in the developer environment.

## Decision
Use `pre-commit` with:
- `pre-commit-hooks` (latest release v6.0.0) for:
  `check-merge-conflict`, `check-added-large-files`, `check-symlinks`,
  `check-json`, `check-yaml`, and `check-toml`.
- `gitleaks` (latest release v8.30.0) for secret scanning via the `gitleaks` hook.

## Notes
- `pre-commit` should be installed by developers (e.g., via `pipx` or `pip`).
- The hook configuration should live in `.pre-commit-config.yaml` at the project
  root so it applies consistently across projects and templates.

## Plan
- Add `.pre-commit-config.yaml` to `templates/` so new projects inherit
  the safety hooks.
- Update `project_setup.md` to copy dotfiles from the template and mention
  `pre-commit install` as a setup step.
- Add `.pre-commit-config.yaml` to existing projects (`arborist`,
  `classic-cli-boardgames`) and document the hook setup in each README.
