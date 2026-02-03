"""Shared navigation command parsing for the CLI."""

from __future__ import annotations

from enum import Enum
from typing import Final, Optional

from classic_cli_boardgames.core.parsing import normalize_text


class NavCommand(str, Enum):
    HELP = "help"
    BACK = "back"
    RESTART = "restart"
    QUIT = "quit"


_NAV_COMMANDS: Final[dict[str, NavCommand]] = {
    NavCommand.HELP.value: NavCommand.HELP,
    NavCommand.BACK.value: NavCommand.BACK,
    NavCommand.RESTART.value: NavCommand.RESTART,
    NavCommand.QUIT.value: NavCommand.QUIT,
}


def parse_navigation_command(text: str) -> Optional[NavCommand]:
    """Return a navigation command if the input matches one, otherwise None."""
    normalized = normalize_text(text)
    if not normalized:
        return None
    return _NAV_COMMANDS.get(normalized)
