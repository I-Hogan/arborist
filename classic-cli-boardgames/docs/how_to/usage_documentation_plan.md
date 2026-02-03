# Usage Documentation Plan

## Goals
- Provide clear, user-facing instructions for running the CLI and navigating games.
- Ensure interactive help text and written docs stay aligned.
- Keep documentation lightweight and easy to maintain.

## Scope
- Add a root README with quickstart, usage, and command overview.
- Add a how-to guide that details navigation commands and move input formats.
- Provide a non-interactive `-h/--help` output for quick reference.
- Update documentation indexes to point to the new guides.

## Approach (best_practices.md)
- Keep the solution simple: reuse existing CLI constants where possible.
- Prefer a single source of truth for help text to reduce drift.
- Avoid heavyweight tooling or dependencies; pure Python and Markdown only.
- Verify formatting and CLI behavior with existing pre-commit tooling.

## Deliverables
- `README.md` in the project root.
- `docs/how_to/using_the_cli.md` for detailed usage.
- `classic_cli_boardgames/cli/help_text.py` (or equivalent) used by CLI and docs.
- Updated `docs/README.md` and `docs/how_to/README.md` indexes.
