"""User-facing help text for the Classic CLI Boardgames."""

APP_TITLE = "Classic CLI Boardgames"

MENU_HELP = (
    "Menu commands:\n  help    Show this menu help\n  quit    Exit the program\n"
)

GAME_HELP = (
    "Game commands:\n"
    "  help    Show game commands\n"
    "  back    Return to the main menu\n"
    "  restart Restart the current game\n"
    "  quit    Exit the program\n"
)

DIFFICULTY_HELP = (
    "Difficulty commands:\n"
    "  help    Show difficulty options\n"
    "  back    Return to the main menu\n"
    "  quit    Exit the program\n"
)

PLAYER_MODE_HELP = (
    "Player selection commands:\n"
    "  help    Show player options\n"
    "  back    Return to the main menu\n"
    "  quit    Exit the program\n"
)

CHESS_HELP = (
    "Chess commands:\n"
    "  help    Show this help\n"
    "  back    Return to the main menu\n"
    "  restart Restart the current game\n"
    "  quit    Exit the program\n"
    "\n"
    "Moves use coordinates:\n"
    "  e2e4       Move a piece\n"
    "  e7e8q      Promote to queen (q/r/b/n)\n"
    "  O-O        Castle kingside\n"
    "  O-O-O      Castle queenside\n"
)

CHECKERS_HELP = (
    "Checkers commands:\n"
    "  help    Show this help\n"
    "  back    Return to the main menu\n"
    "  restart Restart the current game\n"
    "  quit    Exit the program\n"
    "\n"
    "Rules summary:\n"
    "  Captures are mandatory; multi-jump captures must be completed.\n"
    "  Men promote to kings when they end a move on the far row.\n"
    "\n"
    "Moves use coordinates:\n"
    "  b6-a5       Move a piece\n"
    "  b6-d4-f2    Multi-jump capture\n"
    "  b6xd4xf2    Capture with x separators\n"
)

BACKGAMMON_HELP = (
    "Backgammon commands:\n"
    "  help    Show this help\n"
    "  back    Return to the main menu\n"
    "  restart Restart the current game\n"
    "  quit    Exit the program\n"
    "\n"
    "Rules summary:\n"
    "  Enter from the bar before moving other checkers.\n"
    "  Use both dice when possible; doubles give four moves.\n"
    "  Bear off only when all checkers are in the home board.\n"
    "\n"
    "Moves use start/end pairs per die:\n"
    "  24/23 13/11   Two moves using dice order\n"
    "  bar/24 6/off  Enter from bar and bear off\n"
)

GO_HELP = (
    "Go commands:\n"
    "  help    Show this help\n"
    "  back    Return to the main menu\n"
    "  restart Restart the current game\n"
    "  quit    Exit the program\n"
    "\n"
    "Rules summary:\n"
    "  Passing is always allowed; the game ends after two passes.\n"
    "  Simple ko is enforced; suicide is not allowed.\n"
    "\n"
    "Moves use coordinates:\n"
    "  D4        Place a stone\n"
    "  pass      Pass your turn\n"
    "  Coordinates are A-H and J with rows 1-9.\n"
)


def render_cli_help() -> str:
    """Render non-interactive CLI help text."""
    lines = [
        APP_TITLE,
        "",
        "Usage:",
        "  python -m classic_cli_boardgames",
        "  python -m classic_cli_boardgames --help",
        "",
        "Main menu:",
        "  Choose a game by number or name.",
        "  Aliases: Chess (ch), Checkers (draughts, ck), Backgammon (bg), Go (g).",
        "",
        MENU_HELP.rstrip(),
        "",
        "Difficulty selection:",
        "  Press Enter for default: Intermediate.",
        "  Pick by number or name (easy/intermediate/challenging).",
        "",
        DIFFICULTY_HELP.rstrip(),
        "",
        "Player selection:",
        "  Press Enter for default: You vs Computer.",
        "  Pick by number or name (player/auto).",
        "",
        PLAYER_MODE_HELP.rstrip(),
        "",
        "Auto-play runs continuously; type a command and press Enter to interrupt.",
        "",
        CHESS_HELP.rstrip(),
        "",
        CHECKERS_HELP.rstrip(),
        "",
        BACKGAMMON_HELP.rstrip(),
        "",
        GO_HELP.rstrip(),
    ]
    return "\n".join(lines)
