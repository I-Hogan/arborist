# Instructions for reviewing changes

Code review instructions specific to this project. General code review guidelines
should live in the core `arborist/` project.

## Code Review Checklist
- Verify any list file mutations only clear content when all work is complete.
- Confirm project discovery logic ignores hidden folders and `node_modules`.
- Check spawned processes have explicit error handling and timeouts.
- Ensure no destructive filesystem operations (delete/move) without safeguards.
- Validate shell scripts use `set -euo pipefail` and handle missing tools.
- Confirm new logic is covered by at least one fast unit test.
- Ensure docs and indexes are updated when adding new files.

## Code Review Notes
- Use `scripts/pre_commit.sh` before final approval.
