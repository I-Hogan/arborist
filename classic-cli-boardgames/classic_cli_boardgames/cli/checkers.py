"""Checkers CLI loop and input handling."""

from __future__ import annotations

from classic_cli_boardgames.ai.checkers import CheckersAI
from classic_cli_boardgames.cli.ai_setup import prompt_difficulty, prompt_player_mode
from classic_cli_boardgames.cli.auto_input import AutoCommandReader
from classic_cli_boardgames.cli.commands import NavCommand, parse_navigation_command
from classic_cli_boardgames.cli.help_text import CHECKERS_HELP
from classic_cli_boardgames.core.interfaces import AIConfig
from classic_cli_boardgames.games.checkers import (
    CheckersEngine,
    Color,
    parse_move_input,
)

_ENGINE = CheckersEngine()
_AI = CheckersAI(_ENGINE)


def launch_checkers_game() -> bool:
    """Run a checkers game loop. Returns True if the program should exit."""
    difficulty, command = prompt_difficulty("Checkers")
    if command is NavCommand.BACK:
        print("Returning to the main menu.")
        print()
        return False
    if command is NavCommand.QUIT:
        return True

    player_mode, command = prompt_player_mode("Checkers")
    if command is NavCommand.BACK:
        print("Returning to the main menu.")
        print()
        return False
    if command is NavCommand.QUIT:
        return True

    config = AIConfig(difficulty=difficulty)
    ai_vs_ai = player_mode.ai_vs_ai
    human_color = Color.WHITE
    ai_color = human_color.opponent()
    state = _ENGINE.new_game()
    print()
    auto_reader = AutoCommandReader() if ai_vs_ai else None
    if ai_vs_ai:
        print("Starting Checkers. Computer vs Computer.")
        print(f"Computer difficulty: {difficulty.name}. Type 'help' for commands.")
        print("Auto-play is on. Type 'back' for the main menu, or 'help' for commands.")
    else:
        print(f"Starting Checkers. You play as {human_color.label}.")
        print(f"Computer difficulty: {difficulty.name}. Type 'help' for commands.")
    while True:
        print()
        print(_ENGINE.render(state))
        status = _ENGINE.is_terminal(state)
        if status.is_terminal:
            outcome = status.outcome
            if outcome is None:
                print("Game over.")
            elif outcome.winner:
                print(f"Game over: {outcome.winner} wins by {outcome.reason}.")
            else:
                print(f"Game over: draw by {outcome.reason}.")
            raw = input("Checkers> ")
            command = parse_navigation_command(raw)
            if command is None:
                print("Game is over. Type 'restart', 'back', or 'quit'.")
                continue
            if command is NavCommand.HELP:
                print(CHECKERS_HELP)
                continue
            if command is NavCommand.BACK:
                print("Returning to the main menu.")
                print()
                return False
            if command is NavCommand.RESTART:
                print("Restarting the game.")
                state = _ENGINE.new_game()
                continue
            if command is NavCommand.QUIT:
                return True
            print("That command is not available here. Type 'help' for options.")
            continue

        if ai_vs_ai:
            raw = auto_reader.poll() if auto_reader is not None else None
            if raw is not None:
                command = parse_navigation_command(raw)
                if command is not None:
                    if command is NavCommand.HELP:
                        print(CHECKERS_HELP)
                        continue
                    if command is NavCommand.BACK:
                        print("Returning to the main menu.")
                        print()
                        return False
                    if command is NavCommand.RESTART:
                        print("Restarting the game.")
                        state = _ENGINE.new_game()
                        continue
                    if command is NavCommand.QUIT:
                        return True
                    print(
                        "That command is not available here. Type 'help' for options."
                    )
                    continue
                if raw.strip():
                    print(
                        "That command is not available here. Type 'help' for options."
                    )
                    continue
            legal_moves = _ENGINE.legal_moves(state)
            move = _AI.choose_move(state, legal_moves, config)
            print(f"Computer ({state.active_color.label}) plays {move.notation()}.")
            state = _ENGINE.apply_move(state, move)
            continue

        if state.active_color is ai_color:
            legal_moves = _ENGINE.legal_moves(state)
            move = _AI.choose_move(state, legal_moves, config)
            print(f"Computer ({ai_color.label}) plays {move.notation()}.")
            state = _ENGINE.apply_move(state, move)
            continue

        raw = input(f"Checkers ({state.active_color.label})> ")
        command = parse_navigation_command(raw)
        if command is not None:
            if command is NavCommand.HELP:
                print(CHECKERS_HELP)
                continue
            if command is NavCommand.BACK:
                print("Returning to the main menu.")
                print()
                return False
            if command is NavCommand.RESTART:
                print("Restarting the game.")
                state = _ENGINE.new_game()
                continue
            if command is NavCommand.QUIT:
                return True
            print("That command is not available here. Type 'help' for options.")
            continue

        legal_moves = _ENGINE.legal_moves(state)
        move, error = parse_move_input(raw, legal_moves)
        if move is None:
            print(error or "Invalid move.")
            continue
        state = _ENGINE.apply_move(state, move)
