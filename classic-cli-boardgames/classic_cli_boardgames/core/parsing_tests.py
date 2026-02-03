from classic_cli_boardgames.core.parsing import (
    normalize_text,
    parse_alias,
    parse_choice,
    parse_int,
    parse_int_in_range,
    split_tokens,
)


def test_normalize_text() -> None:
    assert normalize_text("  HeLp ") == "help"
    assert normalize_text("\nQuit\t") == "quit"


def test_split_tokens() -> None:
    assert split_tokens("one two") == ["one", "two"]
    assert split_tokens("one 'two three' four") == ["one", "two three", "four"]
    assert split_tokens("") == []


def test_parse_int() -> None:
    assert parse_int("42") == 42
    assert parse_int("  7 ") == 7
    assert parse_int("nope") is None


def test_parse_int_in_range() -> None:
    assert parse_int_in_range("3", 1, 5) == 3
    assert parse_int_in_range("0", 1, 5) is None
    assert parse_int_in_range("nine", 1, 5) is None


def test_parse_choice() -> None:
    choices = ("Help", "Quit")
    assert parse_choice("help", choices) == "Help"
    assert parse_choice(" Quit ", choices) == "Quit"
    assert parse_choice("unknown", choices) is None


def test_parse_alias() -> None:
    aliases = (("yes", "y"), ("no", "n"))
    assert parse_alias("Y", aliases) == 0
    assert parse_alias(" no ", aliases) == 1
    assert parse_alias("maybe", aliases) is None
