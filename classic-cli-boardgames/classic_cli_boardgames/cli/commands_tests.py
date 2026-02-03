from classic_cli_boardgames.cli.app import GameOption, parse_menu_selection
from classic_cli_boardgames.cli.commands import NavCommand, parse_navigation_command


def _noop_launcher() -> bool:
    return False


def test_parse_navigation_command() -> None:
    assert parse_navigation_command("help") == NavCommand.HELP
    assert parse_navigation_command(" Quit ") == NavCommand.QUIT
    assert parse_navigation_command("") is None
    assert parse_navigation_command("unknown") is None


def test_parse_menu_selection_by_number_and_name() -> None:
    options = (
        GameOption("chess", "Chess", ("ch",), _noop_launcher),
        GameOption("checkers", "Checkers", ("ck",), _noop_launcher),
    )
    assert parse_menu_selection("1", options) == options[0]
    assert parse_menu_selection("checkers", options) == options[1]
    assert parse_menu_selection("Chess", options) == options[0]
    assert parse_menu_selection("ch", options) == options[0]
    assert parse_menu_selection("3", options) is None
    assert parse_menu_selection("", options) is None
