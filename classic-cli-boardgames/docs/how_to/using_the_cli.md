# Using the Classic CLI Boardgames

## Start the CLI

From the project root:

```bash
python -m classic_cli_boardgames
```

For non-interactive help:

```bash
python -m classic_cli_boardgames --help
```

## Main menu

- Choose a game by number or by typing the name/alias.
- Menu commands:
  - `help` shows the menu commands.
  - `quit` exits the program.

Game aliases:
- Chess: `chess`, `ch`
- Checkers: `checkers`, `draughts`, `ck`
- Backgammon: `backgammon`, `bg`
- Go: `go`, `g`

## Difficulty selection

- Pick a difficulty by number or name, or press Enter for the default.
- Default: Intermediate.
- Difficulty commands:
  - `help` shows difficulty commands.
  - `back` returns to the main menu.
  - `quit` exits the program.

Difficulty names and aliases:
- Easy: `easy`, `e`, `beginner`
- Intermediate: `intermediate`, `i`, `medium`, `normal`
- Challenging: `challenging`, `c`, `hard`, `advanced`

## Player selection

- Pick a player mode by number or name, or press Enter for the default.
- Default: You vs Computer.
- Player commands:
  - `help` shows player options.
  - `back` returns to the main menu.
  - `quit` exits the program.

Player modes and aliases:
- You vs Computer: `player`, `human`, `you`, `p`
- Computer vs Computer: `auto`, `ai`, `computer`, `cpu`, `c`

When watching the AI play both sides, turns advance automatically. You can
type `help`, `back`, `restart`, or `quit` at any time and press Enter to
interrupt.

## In-game commands

These commands work while you are playing:
- `help` shows the game-specific help text.
- `back` returns to the main menu.
- `restart` resets the current game.
- `quit` exits the program.

## Move input formats

The board shows coordinate labels to guide your input. Commands are
case-insensitive.

### Chess

- Basic move: `e2e4` (hyphens or spaces are ignored, so `e2-e4` also works).
- Promotion: `e7e8q` (use `q`, `r`, `b`, or `n`).
- Castling: `O-O` (kingside) or `O-O-O` (queenside).

### Checkers

- Simple move: `b6-a5` (any separators are fine).
- Multi-jump capture: `b6-d4-f2`.
- Capture with `x` separators: `b6xd4xf2`.

Captures are mandatory when available. If more than one capture path is
possible, enter the full path so the move is unambiguous.

### Backgammon

- Enter moves as start/end pairs separated by spaces.
- Use `/`, `-`, or `->` between start and end.

Examples:
- `24/23 13/11`
- `bar/24 6/off`

Use `bar` when entering from the bar, and `off` when bearing off.

### Go

- Place a stone: `D4` (letters A-H and J with rows 1-9).
- Pass your turn: `pass` (or `p`).

The game ends after two consecutive passes, and simple ko is enforced.
