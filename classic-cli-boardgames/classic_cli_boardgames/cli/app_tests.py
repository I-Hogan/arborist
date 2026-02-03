import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run_cli_session(inputs: list[str]) -> subprocess.CompletedProcess[str]:
    joined = "\n".join(inputs) + "\n"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "classic_cli_boardgames"],
        input=joined,
        text=True,
        capture_output=True,
        cwd=ROOT,
        env=env,
        timeout=20,
    )


def _run_cli_help() -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    return subprocess.run(
        [sys.executable, "-m", "classic_cli_boardgames", "--help"],
        text=True,
        capture_output=True,
        cwd=ROOT,
        env=env,
        timeout=20,
    )


def test_help_flag() -> None:
    result = _run_cli_help()
    assert result.returncode == 0, (
        f"CLI exited with {result.returncode}. stderr: {result.stderr}"
    )
    output = result.stdout
    assert "Classic CLI Boardgames" in output
    assert "Usage:" in output
    assert "Main menu:" in output


def test_menu_help_and_invalid_input() -> None:
    result = _run_cli_session(["help", "bogus", "quit"])
    assert result.returncode == 0, (
        f"CLI exited with {result.returncode}. stderr: {result.stderr}"
    )
    output = result.stdout
    assert "Classic CLI Boardgames" in output
    assert "Menu commands:" in output
    assert "Unknown option." in output
    assert "Goodbye!" in output


@pytest.mark.parametrize(
    ("selection", "game_name"),
    [
        ("1", "Chess"),
        ("2", "Checkers"),
        ("3", "Backgammon"),
        ("4", "Go"),
    ],
)
def test_game_flow_back_to_menu(selection: str, game_name: str) -> None:
    result = _run_cli_session([selection, "", "", "back", "quit"])
    assert result.returncode == 0, (
        f"CLI exited with {result.returncode}. stderr: {result.stderr}"
    )
    output = result.stdout
    assert "Select difficulty:" in output
    assert "Select players:" in output
    assert f"Starting {game_name}." in output
    assert "Returning to the main menu." in output
    assert "Goodbye!" in output


def test_game_flow_auto_mode_back_to_menu() -> None:
    result = _run_cli_session(["1", "1", "2", "back", "quit"])
    assert result.returncode == 0, (
        f"CLI exited with {result.returncode}. stderr: {result.stderr}"
    )
    output = result.stdout
    assert "Select difficulty:" in output
    assert "Select players:" in output
    assert "Starting Chess. Computer vs Computer." in output
    assert "Returning to the main menu." in output
    assert "Goodbye!" in output
