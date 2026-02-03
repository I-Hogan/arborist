# A history of completed work items

## Format

Jan 31, 2026: <work-item>
- details
- details
- ...

The bullet point list should cover things like, what code changes were made, 
brief explanations of decisions, etc.

## Log (add new logs at the top)

Feb 1, 2026: Added controlled AI score jitter for more varied computer play
- Introduced per-game score jitter in chess, checkers, backgammon, and Go move selection.
- Reused seeded RNGs for deterministic jitter when a seed is provided.
- Kept tie-breaking randomized via the same RNG for consistent replay behavior.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Feb 1, 2026: Added the Go boardgame across rules, AI, CLI, web UI, and docs
- Implemented a 9x9 Go rules engine with area scoring, simple ko, and pass handling.
- Added an intermediate-strength Go AI with heuristic evaluation and deterministic seeding support.
- Integrated Go into the CLI menu, help text, move parsing, and game loop behavior.
- Added Go support in the web UI session manager and board rendering (including styling).
- Documented Go rules and usage details, and verified tests via `scripts/pre_commit.sh`.

Jan 31, 2026: Verified modern web UI board visuals and stabilized test runs
- Confirmed the web UI board renderer uses styled grids, piece elements, and metadata notes for turn/dice/bar/off/check alerts.
- Skipped web server tests when socket permissions prevent binding a local port.
- Added a pytest-xdist fallback to rerun tests without xdist if the parallel run fails.
- Verified `scripts/pre_commit.sh` runs cleanly after the updates.

Jan 31, 2026: Added a local web UI for game selection and play
- Added a lightweight HTTP server and session manager for running the web UI locally.
- Built a modern static interface with setup controls, board rendering, move entry, and match logs.
- Wired AI controls for single-step and auto-play in AI vs AI mode.
- Added web-focused tests for the server and session lifecycle.
- Documented how to launch the web UI from the project README.

Jan 31, 2026: Enabled auto-play for computer vs computer mode
- Added a non-blocking auto command reader for auto-play input handling.
- Updated chess, checkers, and backgammon loops to advance automatically while accepting nav commands.
- Refreshed CLI help text, usage docs, and CLI integration coverage for auto-play.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: Added user-facing CLI help and usage documentation
- Added a root README plus a CLI usage guide covering menus, commands, and move formats.
- Centralized CLI help text in a shared module and reused it across menu/difficulty/game prompts.
- Added a `--help` option with non-interactive usage output and integration coverage.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: Added CLI integration tests for menu navigation and game flow
- Added subprocess-driven CLI integration coverage for menu help and invalid input handling.
- Added per-game start/back/quit integration coverage for Chess, Checkers, and Backgammon.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: Added unit tests for rules, move generation, and AI determinism
- Added unit tests for chess castling, en passant, and initial legal moves.
- Added checkers coverage for mandatory captures, multi-jumps, and promotion rules.
- Added backgammon tests for bar entry, bearing off, and high-die move selection.
- Added deterministic AI selection tests for chess, checkers, and backgammon.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: Added intermediate AI opponents with difficulty selection
- Added shared difficulty presets plus a CLI prompt for selecting AI strength.
- Implemented chess and checkers alpha-beta AI with positional heuristics and mobility scoring.
- Implemented a backgammon AI with dice-aware evaluation and pip-count heuristics.
- Integrated AI turns into each game loop with move announcements.
- Added explicit-dice move application helpers for backgammon AI search.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: Implemented backgammon rules, dice handling, and CLI rendering
- Added a backgammon engine with bar/off tracking, dice expansion, and legal move generation.
- Implemented bearing off, bar entry, and hit handling with dice-order sequencing.
- Added backgammon board rendering with top/bottom point grids plus bar/off counts.
- Added a backgammon CLI loop with move parsing, pass handling, and menu integration.
- Documented backgammon rules notes and an implementation plan.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: Implemented checkers rules, move generation, and CLI rendering
- Added a checkers engine with mandatory captures, multi-jump sequences, promotion, and terminal detection.
- Implemented ASCII board rendering with coordinates and capture-available messaging.
- Added a checkers CLI loop with move parsing, help text, and menu integration.
- Documented the checkers rules implementation plan and updated the concepts index.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: Implemented chess rules, move generation, and CLI rendering
- Added a chess engine with immutable state, legal move generation, and checkmate/stalemate detection.
- Implemented castling, en passant, and promotion handling alongside check-safe move filtering.
- Added ASCII board rendering with coordinates and in-check messaging.
- Added a chess CLI loop with move parsing and navigation commands.
- Documented chess engine representation choices and an implementation plan.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: Built shared core utilities for parsing, validation, RNG, and rendering
- Added grid rendering helpers with row/column labels and coordinate utilities.
- Expanded core validation helpers for range checks, non-empty input, and rectangular grids.
- Updated CLI parsing to rely on shared parsing helpers for menu selection and commands.
- Added unit tests covering RNG seeding, parsing helpers, validation additions, and rendering output.
- Verified `scripts/pre_commit.sh` runs cleanly in the current environment.

Jan 31, 2026: Added game/AI package scaffolding and shared interfaces
- Added `games/` and `ai/` packages with exports for shared interfaces.
- Defined game/AI protocols and shared data structures in `core/interfaces.py`.
- Updated core exports to surface the shared interfaces.
- Verified `scripts/pre_commit.sh` runs cleanly after changes.

Jan 31, 2026: CLI entry menu and routing scaffolding
- Added CLI entry modules, navigation command parsing, and a main menu loop.
- Implemented stub game loops for Chess, Checkers, and Backgammon routing.
- Added a CLI concept note and updated the concepts index.
- Added focused unit tests for command parsing and menu selection helpers.

Jan 31, 2026: Project setup tooling and starter tests
- Added style/test/pre-commit scripts with ruff/pytest-first execution and safe fallbacks.
- Added starter package structure plus a core validation helper.
- Added a basic unit test using unittest (compatible with pytest).
- Populated the code review checklist for non-automated checks.
- Recorded MVP work items for future implementation.
- Verified `scripts/pre_commit.sh` runs cleanly in the current environment.
