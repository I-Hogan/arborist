# Web GUI Plan

## Goals
- Provide a local web UI for selecting and playing Chess, Checkers, Backgammon, and Go.
- Reuse existing game rules and AI logic.
- Keep dependencies minimal and align with the current CLI behavior.

## Architecture
- `classic_cli_boardgames/web/server.py`: Threading HTTP server with JSON API + static assets.
- `classic_cli_boardgames/web/sessions.py`: Session management, game adapters, and move handling.
- `classic_cli_boardgames/web/static/`: `index.html`, `app.css`, `app.js` for the UI.
- Entry point: `python -m classic_cli_boardgames.web`.

## API Shape
- `GET /api/options`: games, difficulties, player modes, help text.
- `POST /api/session`: create session with game + difficulty + mode.
- `POST /api/session/<id>/action`: submit move, restart, help, or AI step.

## UI Flow
- Landing panel for game selection, difficulty, and player mode.
- Board rendered in a preformatted area with status + last action.
- Move input box (text command) and action buttons (restart, end, help).
- AI-vs-AI mode supports step + optional auto-play loop from the client.

## Testing
- Unit tests for session creation and move validation per game.
- Lightweight API tests to ensure JSON responses and state transitions.

## Docs
- Update README with web launch instructions.
- Add how-to guide for using the web UI.
- Record work log entry once complete.
