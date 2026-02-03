# Go engine and UI plan

## Goals
- Add Go (9x9) to the CLI and web UI with consistent navigation commands.
- Keep the rules deterministic and fast for tests.
- Reuse the existing engine/AI interfaces and menu flows.

## Engine plan
- Define `GoState` with board, active color, capture counts, pass count, and previous board.
- Implement legal moves:
  - Allow pass.
  - Allow placements on empty points that are not suicide and do not violate simple ko.
- Implement captures by removing opponent groups with zero liberties after a move.
- End the game after two consecutive passes.
- Score using area scoring (stones + territory), no komi.

## AI plan
- Implement a shallow minimax/alpha-beta search with node caps from difficulty.
- Evaluate with area score difference and light capture incentive.
- Respect deterministic seeds via existing RNG helpers.

## CLI + Web plan
- Add Go to the main menu and help text.
- Create a CLI loop similar to other games.
- Add a Go definition to the web session registry.
- Render Go stones in the web UI with a compact grid style.

## Tests + Docs plan
- Add Go rule tests (capture, suicide, pass/end).
- Update CLI/web usage docs and README to mention Go.
- Ensure web UI text mentions the new game.
