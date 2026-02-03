# Project Specification

## Vision
Deliver a user-friendly command-line hub that lets a player pick a classic
board game, play against an intermediate-strength computer opponent, or watch
the AI play both sides.

## Goals
- Single entry script that launches a menu of games.
- Consistent, minimal navigation commands (help, back, quit, restart).
- Four classic, widely recognized board games at launch.
- Computer opponent that challenges an intermediate player.
- Local web UI for selecting and playing games alongside the CLI.
- Clean separation between UI, rules engine, and AI logic.
- Fast unit tests and reproducible CLI integration tests.

## Non-goals (initially)
- Networked multiplayer.
- Advanced/competitive engine strength beyond "intermediate".
- Save/load profiles or long-term stats.

## Initial Game Lineup
1. Chess (standard rules).
2. Checkers (American/English draughts rules).
3. Backgammon (standard rules with dice).
4. Go (9x9, area scoring).

## User Experience
- Menu-driven selection: numeric choices + short text commands.
- Player selection: choose human vs AI or computer vs computer.
- In-game commands (case-insensitive):
  - `help`: show rules summary + input format.
  - `back`: return to main menu.
  - `restart`: restart current game.
  - `quit`: exit the program.
- Clear board rendering with coordinates and move prompts.
- Input validation with actionable error messages.

## Architecture
- `cli/` module: rendering, prompts, and command routing.
- `games/` package: one module per game with shared interface:
  - `new_game()` -> game state
  - `legal_moves(state)` -> list
  - `apply_move(state, move)` -> new state
  - `is_terminal(state)` -> bool + result
  - `render(state)` -> string/lines
- `ai/` package: per-game AI adapters implementing:
  - move selection with depth/time limits
  - heuristic evaluation
- `core/` utilities: RNG, parsing, and shared data structures.

## AI Approach (Intermediate)
- Chess and Checkers: minimax with alpha-beta pruning, depth-limited.
- Backgammon: expectiminimax with heuristic evaluation and dice roll model.
- Add configurable difficulty presets that adjust depth and evaluation weights.
- Always allow deterministic mode for tests via seeded RNG.

## Tooling and Code Quality
- Language: Python 3.x (latest stable at setup time).
- Formatting + linting: Ruff (format + lint).
- Testing: pytest for unit tests and CLI integration tests.
- Optional type checking: mypy (added when coverage makes sense).

## Testing Strategy
- Unit tests for move generation, rule enforcement, and evaluations.
- Deterministic AI tests using fixed seeds and fixed depth.
- CLI integration tests using subprocess with scripted input.
- All fast tests must run in under 1 second total when possible.

## Project Structure (proposed)
- `classic_cli_boardgames/`
  - `__init__.py`
  - `cli/`
  - `games/`
  - `ai/`
  - `core/`
  - `*_tests.py` files live beside the modules they cover
- `scripts/` for style/test/pre_commit helpers
- `docs/` for research, concepts, and how-to guides
