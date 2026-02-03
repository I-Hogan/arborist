"""CLI entry for launching classic board games."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from classic_cli_boardgames.cli.backgammon import launch_backgammon_game
from classic_cli_boardgames.cli.chess import launch_chess_game
from classic_cli_boardgames.cli.checkers import launch_checkers_game
from classic_cli_boardgames.cli.go import launch_go_game
from classic_cli_boardgames.cli.commands import NavCommand, parse_navigation_command
from classic_cli_boardgames.cli.help_text import APP_TITLE, GAME_HELP, MENU_HELP
from classic_cli_boardgames.core.parsing import parse_alias, parse_int_in_range


@dataclass(frozen=True)
class GameOption:
    key: str
    name: str
    aliases: tuple[str, ...]
    launcher: Callable[[], bool]


WELCOME_TEXT = APP_TITLE
MENU_HINT = "Type a number to select a game, or 'help' for commands."


def run() -> None:
    """Run the CLI main menu loop."""
    print(WELCOME_TEXT)
    print()
    while True:
        menu_text = render_menu(GAME_OPTIONS)
        print(menu_text)
        raw = input("Menu> ")
        command = parse_navigation_command(raw)
        if command is not None:
            if command is NavCommand.HELP:
                print(MENU_HELP)
                continue
            if command is NavCommand.QUIT:
                print("Goodbye!")
                return
            print("That command is not available here. Type 'help' for options.")
            continue

        selection = parse_menu_selection(raw, GAME_OPTIONS)
        if selection is None:
            print("Unknown option. " + MENU_HINT)
            continue

        should_quit = selection.launcher()
        if should_quit:
            print("Goodbye!")
            return


def render_menu(options: Iterable[GameOption]) -> str:
    """Render the main menu text."""
    lines = ["Available games:"]
    for index, option in enumerate(options, start=1):
        lines.append(f"  {index}. {option.name}")
    lines.append("")
    lines.append(MENU_HINT)
    return "\n".join(lines)


def parse_menu_selection(
    text: str, options: Iterable[GameOption]
) -> Optional[GameOption]:
    """Parse a menu selection by number or name."""
    options_list = list(options)
    index = parse_int_in_range(text, 1, len(options_list))
    if index is not None:
        return options_list[index - 1]

    alias_groups = tuple(
        (option.key, option.name, *option.aliases) for option in options_list
    )
    match_index = parse_alias(text, alias_groups)
    if match_index is None:
        return None
    return options_list[match_index]


def launch_stub_game(name: str) -> bool:
    """Placeholder game loop until full games are implemented."""
    print()
    print(f"{name} is not implemented yet.")
    print("Type 'help' for available commands.")
    while True:
        raw = input(f"{name}> ")
        command = parse_navigation_command(raw)
        if command is None:
            print("Moves are not available yet. Type 'help' for commands.")
            continue
        if command is NavCommand.HELP:
            print(GAME_HELP)
            continue
        if command is NavCommand.BACK:
            print("Returning to the main menu.")
            print()
            return False
        if command is NavCommand.RESTART:
            print("Restarting the game.")
            continue
        if command is NavCommand.QUIT:
            return True


GAME_OPTIONS = (
    GameOption("chess", "Chess", ("ch",), launch_chess_game),
    GameOption("checkers", "Checkers", ("draughts", "ck"), launch_checkers_game),
    GameOption("backgammon", "Backgammon", ("bg",), launch_backgammon_game),
    GameOption("go", "Go", ("g",), launch_go_game),
)
