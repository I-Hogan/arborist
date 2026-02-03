"""CLI helpers for configuring AI opponents."""

from __future__ import annotations

from dataclasses import dataclass

from classic_cli_boardgames.ai.difficulty import DEFAULT_DIFFICULTY, DIFFICULTY_OPTIONS
from classic_cli_boardgames.cli.commands import NavCommand, parse_navigation_command
from classic_cli_boardgames.cli.help_text import DIFFICULTY_HELP, PLAYER_MODE_HELP
from classic_cli_boardgames.core.parsing import parse_alias, parse_int_in_range


@dataclass(frozen=True)
class PlayerModeOption:
    key: str
    name: str
    aliases: tuple[str, ...]
    description: str
    ai_vs_ai: bool


PLAYER_MODE_OPTIONS = (
    PlayerModeOption(
        "player",
        "You vs Computer",
        ("human", "you", "p"),
        "Play as White against the AI.",
        False,
    ),
    PlayerModeOption(
        "auto",
        "Computer vs Computer",
        ("ai", "computer", "cpu", "c"),
        "Watch the AI play both sides.",
        True,
    ),
)
DEFAULT_PLAYER_MODE = PLAYER_MODE_OPTIONS[0]


def render_difficulty_menu() -> str:
    """Render difficulty options for the CLI."""
    lines = ["Select difficulty:"]
    for index, option in enumerate(DIFFICULTY_OPTIONS, start=1):
        lines.append(f"  {index}. {option.name} - {option.description}")
    lines.append("")
    lines.append(f"Press Enter for default: {DEFAULT_DIFFICULTY.name}.")
    lines.append("Type 'help' for difficulty commands.")
    return "\n".join(lines)


def prompt_difficulty(game_name: str):
    """Prompt for a difficulty selection; returns (difficulty, nav_command)."""
    print(render_difficulty_menu())
    while True:
        raw = input(f"{game_name} difficulty> ")
        if not raw.strip():
            return DEFAULT_DIFFICULTY, None
        command = parse_navigation_command(raw)
        if command is not None:
            if command is NavCommand.HELP:
                print(DIFFICULTY_HELP)
                continue
            if command in (NavCommand.BACK, NavCommand.QUIT):
                return None, command
            print("That command is not available here. Type 'help' for options.")
            continue

        index = parse_int_in_range(raw, 1, len(DIFFICULTY_OPTIONS))
        if index is not None:
            return DIFFICULTY_OPTIONS[index - 1].difficulty, None

        alias_groups = tuple(
            (option.key, option.name, *option.aliases) for option in DIFFICULTY_OPTIONS
        )
        match = parse_alias(raw, alias_groups)
        if match is not None:
            return DIFFICULTY_OPTIONS[match].difficulty, None

        print("Unknown difficulty. Enter a number or name.")


def render_player_mode_menu() -> str:
    """Render the player mode options for the CLI."""
    lines = ["Select players:"]
    for index, option in enumerate(PLAYER_MODE_OPTIONS, start=1):
        lines.append(f"  {index}. {option.name} - {option.description}")
    lines.append("")
    lines.append(f"Press Enter for default: {DEFAULT_PLAYER_MODE.name}.")
    lines.append("Type 'help' for player commands.")
    return "\n".join(lines)


def parse_player_mode(text: str) -> PlayerModeOption | None:
    """Parse a player mode selection by number or name."""
    index = parse_int_in_range(text, 1, len(PLAYER_MODE_OPTIONS))
    if index is not None:
        return PLAYER_MODE_OPTIONS[index - 1]

    alias_groups = tuple(
        (option.key, option.name, *option.aliases) for option in PLAYER_MODE_OPTIONS
    )
    match = parse_alias(text, alias_groups)
    if match is not None:
        return PLAYER_MODE_OPTIONS[match]
    return None


def prompt_player_mode(game_name: str):
    """Prompt for player mode; returns (mode, nav_command)."""
    print(render_player_mode_menu())
    while True:
        raw = input(f"{game_name} players> ")
        if not raw.strip():
            return DEFAULT_PLAYER_MODE, None
        command = parse_navigation_command(raw)
        if command is not None:
            if command is NavCommand.HELP:
                print(PLAYER_MODE_HELP)
                continue
            if command in (NavCommand.BACK, NavCommand.QUIT):
                return None, command
            print("That command is not available here. Type 'help' for options.")
            continue

        selection = parse_player_mode(raw)
        if selection is not None:
            return selection, None

        print("Unknown selection. Enter a number or name.")
