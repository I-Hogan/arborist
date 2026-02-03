"""Core shared utilities."""

from classic_cli_boardgames.core.parsing import (
    normalize_text,
    parse_alias,
    parse_choice,
    parse_int,
    parse_int_in_range,
    split_tokens,
)
from classic_cli_boardgames.core.rendering import (
    alphabetic_labels,
    numeric_labels,
    render_grid,
)
from classic_cli_boardgames.core.rng import create_rng
from classic_cli_boardgames.core.interfaces import (
    AIDifficulty,
    AIConfig,
    AIEngine,
    GameEngine,
    GameOutcome,
    TerminalStatus,
)
from classic_cli_boardgames.core.validation import (
    clamp_int,
    require_in_range,
    require_non_empty,
    require_rectangular_grid,
)

__all__ = [
    "AIDifficulty",
    "AIConfig",
    "AIEngine",
    "GameEngine",
    "GameOutcome",
    "TerminalStatus",
    "alphabetic_labels",
    "clamp_int",
    "create_rng",
    "normalize_text",
    "numeric_labels",
    "parse_alias",
    "parse_choice",
    "parse_int",
    "parse_int_in_range",
    "render_grid",
    "require_in_range",
    "require_non_empty",
    "require_rectangular_grid",
    "split_tokens",
]
