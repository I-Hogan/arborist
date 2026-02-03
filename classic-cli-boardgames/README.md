# Classic CLI Boardgames

Classic CLI Boardgames is a command-line hub for playing Chess, Checkers,
Backgammon, and Go against a computer opponent, or watching the computer play
itself.

## Quickstart

Requirements: Python 3.x.

From the project root:

```bash
./scripts/setup.sh
```

Activate the virtual environment if desired:

```bash
source .venv/bin/activate
```

Run the CLI:

```bash
python -m classic_cli_boardgames
```

For a quick reference, run:

```bash
python -m classic_cli_boardgames --help
```

## Web UI

Run the local web UI server:

```bash
python -m classic_cli_boardgames.web
```

Then open `http://127.0.0.1:8000` in your browser.

## How to play

- Select a game by number or name (aliases also work).
- Choose a difficulty by number or name, or press Enter for the default.
- Choose whether you want to play or watch the AI play both sides.
- Use `help`, `back`, `restart`, and `quit` commands as shown in the prompts.

Game aliases:
- Chess: `chess`, `ch`
- Checkers: `checkers`, `draughts`, `ck`
- Backgammon: `backgammon`, `bg`
- Go: `go`, `g`

Move formats and detailed command behavior are in:
- `docs/how_to/using_the_cli.md`

## More documentation
- `docs/README.md`
