# Using the Web UI

## Start the server

From the project root, run:

```bash
python -m classic_cli_boardgames.web
```

Open `http://127.0.0.1:8000` in your browser. Stop the server with Ctrl+C in
that terminal.

## Start a match

1. Pick a game, difficulty, and player mode.
2. Select **Start game**.
3. The board will render on the right.

## Controls and actions

- Move input uses the same formats as the CLI. Examples:
  - Chess: `e2e4`, `O-O`
  - Checkers: `b6-a5`, `b6-d4-f2`
  - Backgammon: `24/23 13/11`
  - Go: `D4`, `pass`
- **Restart** resets the current match.
- **End** closes the session and clears the board.
- **Help** shows command and move reminders for the selected game.

## AI vs AI mode

When you choose Computer vs Computer:

- **Next move (AI)** advances a single turn.
- **Auto-play** runs continuous turns until the game ends or you toggle it off.

## Troubleshooting

- If the UI looks stuck, check the terminal running the server for errors.
- If a move is rejected, confirm it matches the CLI move format for the game.
