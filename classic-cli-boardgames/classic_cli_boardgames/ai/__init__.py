"""AI modules and shared AI interfaces."""

from classic_cli_boardgames.ai.backgammon import BackgammonAI
from classic_cli_boardgames.ai.checkers import CheckersAI
from classic_cli_boardgames.ai.chess import ChessAI
from classic_cli_boardgames.ai.go import GoAI
from classic_cli_boardgames.ai.difficulty import (
    DEFAULT_DIFFICULTY,
    DIFFICULTY_OPTIONS,
    DifficultyOption,
)
from classic_cli_boardgames.core.interfaces import AIDifficulty, AIConfig, AIEngine

__all__ = [
    "AIDifficulty",
    "AIConfig",
    "AIEngine",
    "BackgammonAI",
    "CheckersAI",
    "ChessAI",
    "GoAI",
    "DEFAULT_DIFFICULTY",
    "DIFFICULTY_OPTIONS",
    "DifficultyOption",
]
