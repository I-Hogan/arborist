# Template layout check plan

## Goal
Ensure Arborist's file checks validate that template files live in their
expected locations after the template move.

## Plan
- Add a fast Node test that inspects `templates/` at repo root.
- Assert the root `templates/` directory contains the expected subdirectories
  (`arborist`, `docs`, `experiments`, `scripts`) plus `.pre-commit-config.yaml`.
- Assert the base template files live under `templates/arborist` and are
  present as files.
- Rely on `scripts/pre_commit.sh` so the check runs alongside the fast test
  suite.

## Implementation plan (2026-02-03)
- Add the missing standard list file to the templates and align the Arborist
  project layout with it.
- Centralize template requirements in a small Node module so the runner and
  tests share the same expectations.
- Validate the template layout once at runner startup and validate each project
  layout before processing, surfacing any missing files or directories.
- Keep checks fast (simple filesystem stats) and covered by unit tests.
