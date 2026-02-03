# Checkers rules implementation plan

## Goals
- Implement American/English draughts rules with legal move generation.
- Provide clear ASCII rendering with coordinates.
- Enable a simple CLI loop for manual play (until AI arrives).

## Approach
- **Keep it simple:** Use an 8x8 grid of piece objects and immutable state.
- **Separation of concerns:**
  - `games/checkers.py` owns rules, state, move generation, and rendering.
  - `cli/checkers.py` owns input parsing and the game loop.
- **Determinism:** No randomness in rule logic; moves are generated from state only.

## State model
- `CheckersState` dataclass (frozen): board, active color.
- `Piece` dataclass: color + kind (man/king).
- `Move` dataclass: path (sequence of positions) + captured positions.

## Rules to implement
- Pieces move diagonally on dark squares only.
- Men move/capture forward; kings move/capture both directions.
- Captures are mandatory when available.
- Multi-jump captures are required; moves list full capture sequences.
- Promotion to king when a man ends a move on the far rank (no extra jumps after promotion).
- Terminal detection when a player has no legal moves.

## Rendering
- ASCII board using `core.rendering.render_grid`.
- Row labels 8..1, column labels A..H.
- Pieces: `w`/`W` for white (man/king), `b`/`B` for black.
- Empty dark squares as `.`, light squares as blanks.

## CLI loop
- Prompt for moves using coordinate paths: `b6-a5` or `b6-d4-f2`.
- Accept separators `-`/`x`/whitespace and parse by coordinate tokens.
- Support navigation commands (help/back/restart/quit).
- Validate inputs with actionable errors (including capture-required messaging).

## Testing (future work)
- Unit tests for move generation, capture requirements, and promotion rules.
- CLI integration tests once the loop stabilizes.
