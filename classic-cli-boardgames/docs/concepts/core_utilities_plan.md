# Core Utilities Plan

## Goals
- Provide shared RNG helpers with optional deterministic seeding.
- Centralize input parsing/normalization utilities for CLI and games.
- Expand validation helpers for common CLI/game checks.
- Add board rendering helpers for consistent text grids.

## Approach (best_practices.md)
- Keep the toolset simple: rely only on Python standard library.
- Centralize helpers in `classic_cli_boardgames/core/` so future games/AI share them.
- Add focused unit tests for the new helpers to keep fast feedback.

## Implementation Steps
1. Add `core/rng.py`, `core/parsing.py`, and `core/rendering.py` modules.
2. Extend `core/validation.py` with common validation helpers.
3. Update CLI parsing to use the shared parsing utilities.
4. Add unit tests covering RNG seeding, parsing, validation, and rendering helpers.
