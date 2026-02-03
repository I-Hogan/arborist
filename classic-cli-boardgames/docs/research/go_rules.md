# Go rules and variant choices

## Goals
- Add a playable Go experience that fits the existing CLI/web UI and stays fast.
- Keep rules understandable and deterministic for tests.

## Board size
- Use 9x9 for readability in the terminal and web UI.
- Coordinates use letters A-H and J (skipping I) with rows 1-9 from bottom to top.

## Rule scope
- Legal move: place on an empty intersection.
- Suicide is not allowed unless it captures opposing stones.
- Simple ko only: a move that recreates the previous board position is illegal.
- Passing is always allowed.
- Game ends after two consecutive passes.

## Scoring
- Area scoring (stones on board + surrounded territory).
- No komi for now to keep scoring straightforward.

## Notes
- Captured stone counts are tracked for feedback, but scoring uses area only.
