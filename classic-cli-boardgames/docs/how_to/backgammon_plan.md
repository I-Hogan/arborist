# Backgammon Implementation Plan

## Goals
- Implement standard backgammon rules with dice handling and legal move generation.
- Render a readable board view in an 80-column terminal.
- Add CLI loop with navigation commands consistent with other games.

## Approach
- Keep data structures simple: use Python standard library only.
- Store the board as a 24-length tuple of integers (positive = White, negative = Black).
- Track bar and borne-off counts separately in the game state.
- Generate legal moves by enumerating all dice sequences, applying moves to cloned states.
- Keep rendering isolated in the game module and reuse core rendering helpers where helpful.

## Implementation Steps
1. Add `games/backgammon.py` with state, move, rules, and rendering.
2. Add `cli/backgammon.py` with input parsing and game loop.
3. Wire the CLI menu to launch the backgammon game.
4. Validate via `scripts/pre_commit.sh` and manual playthrough.
