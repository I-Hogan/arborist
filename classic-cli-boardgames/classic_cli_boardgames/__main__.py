"""Module entry point for running the CLI via python -m classic_cli_boardgames."""

from __future__ import annotations

import sys
from typing import Sequence

from classic_cli_boardgames.cli.app import run
from classic_cli_boardgames.cli.help_text import render_cli_help


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI or show non-interactive help."""
    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        if any(arg in ("-h", "--help") for arg in args):
            print(render_cli_help())
            return 0
        print("Unknown option. Use --help for usage.")
        return 2
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
