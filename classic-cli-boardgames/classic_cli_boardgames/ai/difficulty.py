"""Difficulty presets shared across game AIs."""

from __future__ import annotations

from dataclasses import dataclass

from classic_cli_boardgames.core.interfaces import AIDifficulty


@dataclass(frozen=True)
class DifficultyOption:
    """Descriptor used by the CLI to present difficulty choices."""

    key: str
    name: str
    aliases: tuple[str, ...]
    difficulty: AIDifficulty
    description: str


DIFFICULTY_OPTIONS = (
    DifficultyOption(
        key="easy",
        name="Easy",
        aliases=("e", "beginner"),
        difficulty=AIDifficulty("Easy", max_depth=1, max_nodes=400),
        description="Quick lookahead with simple tactics.",
    ),
    DifficultyOption(
        key="intermediate",
        name="Intermediate",
        aliases=("i", "medium", "normal"),
        difficulty=AIDifficulty("Intermediate", max_depth=2, max_nodes=1200),
        description="Balanced lookahead and evaluations.",
    ),
    DifficultyOption(
        key="challenging",
        name="Challenging",
        aliases=("c", "hard", "advanced"),
        difficulty=AIDifficulty("Challenging", max_depth=3, max_nodes=4000),
        description="Deeper lookahead with tighter pruning.",
    ),
)

DEFAULT_DIFFICULTY = DIFFICULTY_OPTIONS[1].difficulty
