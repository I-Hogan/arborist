# Runtime Challenges

- `complete_next_item.md` instructs removing feedback entries after adding todo items, but `AGENTS.md` forbids removing feedback until addressed. Keeping feedback until work items are completed.
- `scripts/pre_commit.sh` failed because `pre-commit` could not fetch `pre-commit-hooks` (no network access to github.com).
- `pre-commit install --config .pre-commit-config.yaml` failed due to a readonly pre-commit cache/database and permission errors writing logs under `/home/hogan/.cache/pre-commit`.
- `pre-commit install` succeeded after setting `PRE_COMMIT_HOME=/tmp/arborist-pre-commit` to avoid the readonly cache path.
- 2026-02-04: `scripts/pre_commit.sh` failed running pre-commit hooks because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
