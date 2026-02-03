# Chess rules implementation plan

## Goals
- Implement standard chess rules with legal move generation.
- Provide clear ASCII rendering with coordinates.
- Enable a simple CLI loop for manual play (until AI arrives).

## Approach
- **Keep it simple:** Use an 8x8 grid of piece objects and immutable state.
- **Separation of concerns:**
  - `games/chess.py` owns rules, state, move generation, and rendering.
  - `cli/chess.py` owns input parsing and the game loop.
- **Determinism:** No randomness in rule logic; moves are generated from state only.

## State model
- `ChessState` dataclass (frozen): board, active color, castling rights, en-passant target,
  halfmove clock (optional), fullmove count.
- `Piece` dataclass: color + kind.
- `Move` dataclass: from/to, promotion, flags (castling, en passant).

## Rules to implement
- Piece movement for all six piece types.
- Captures, including en passant.
- Promotion to Q/R/B/N.
- Castling with full legality checks (no check, no passing through check).
- Check detection and legal-move filtering.
- Terminal detection via checkmate and stalemate.

## Rendering
- ASCII board using `core.rendering.render_grid`.
- Row labels 8..1, column labels A..H.
- Pieces: uppercase (white) / lowercase (black), empty squares as `.`.

## CLI loop
- Prompt for moves using algebraic coordinates: `e2e4`, `e7e8q`, `O-O`/`O-O-O`.
- Accept standard navigation commands (help/back/restart/quit).
- Validate inputs and provide actionable errors.

## Testing (future work)
- Unit tests for move generation, check detection, and special rules.
- CLI integration tests once game loop stabilizes.
