# Runtime Challenges

- `complete_next_item.md` instructs removing feedback entries after adding todo items, but `AGENTS.md` forbids removing feedback until addressed. Keeping feedback until work items are completed.
- `scripts/pre_commit.sh` failed because `pre-commit` could not fetch `pre-commit-hooks` (no network access to github.com).
- `pre-commit install --config .pre-commit-config.yaml` failed due to a readonly pre-commit cache/database and permission errors writing logs under `/home/hogan/.cache/pre-commit`.
- `pre-commit install` succeeded after setting `PRE_COMMIT_HOME=/tmp/arborist-pre-commit` to avoid the readonly cache path.
- 2026-02-04: `scripts/pre_commit.sh` failed running pre-commit hooks because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-04: `pre-commit install --config .pre-commit-config.yaml` failed due to a readonly pre-commit cache and permission errors writing to `/home/hogan/.cache/pre-commit`.
- 2026-02-05: `scripts/pre_commit.sh` failed running pre-commit hooks because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `scripts/pre_commit.sh` failed again while updating project controls UI because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `scripts/pre_commit.sh` failed during pre-commit hook install because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `scripts/pre_commit.sh` failed again while finalizing save state updates because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `scripts/pre_commit.sh` failed during the ChatGPT-style UI refresh because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `scripts/pre_commit.sh` failed while moving Session Status and Save State into the left sidebar because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `scripts/pre_commit.sh` failed during the Astro migration follow-up because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `scripts/pre_commit.sh` failed while re-validating the Astro migration todo because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `scripts/pre_commit.sh` failed while highlighting the active feedback queue item because git could not fetch `https://github.com/pre-commit/pre-commit-hooks/` (Could not resolve host: github.com).
- 2026-02-05: `npm run ui:build` failed with an Astro bundling error for `<script src="/app.js">`; resolved by adding the `is:inline` directive in `web_ui/src/pages/index.astro`.
- 2026-02-06: Local validation via `node scripts/web_ui.mjs` failed in the sandbox with `listen EPERM 127.0.0.1:7788`, so route checks were verified via build output and code inspection instead of live `curl`.
