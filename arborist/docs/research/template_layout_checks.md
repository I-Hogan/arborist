# Template layout check plan

## Goal
Ensure Arborist's file checks validate that template files live in their
expected locations after the template move.

## Plan
- Add a fast Node test that inspects `templates/` at repo root.
- Assert the root `templates/` directory only contains the expected
  subdirectories (`arborist`, `docs`, `experiments`, `scripts`).
- Assert the base template files live under `templates/arborist` and are
  present as files.
- Rely on the existing `scripts/test.sh` runner so the check executes during
  `scripts/pre_commit.sh`.
