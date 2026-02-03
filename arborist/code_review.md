# Manual Code Review Checklist

## Style & Consistency
- Confirm new scripts follow existing Bash conventions (`set -euo pipefail`, `common.sh` helpers).
- Ensure new Node modules are ESM, use consistent import style, and follow Biome formatting.
- Verify documentation updates include any new commands, files, or workflow changes.

## Functional Checks
- Validate discovery logic only targets intended project directories and ignores ignored paths.
- Confirm Codex prompts include required instructions and correct project paths.
- Check timeout behavior: graceful termination, retries, and no orphaned processes.
- Ensure list-file clearing only happens when work is truly complete and no timeouts occurred.
- Review file I/O for safe defaults (no destructive deletes; preserve headers in list files).
- Confirm error handling logs actionable messages and exits with non-zero status on failure.
