"""Module entry point for running the web UI via python -m classic_cli_boardgames.web."""

from classic_cli_boardgames.web.server import main


if __name__ == "__main__":
    raise SystemExit(main())
