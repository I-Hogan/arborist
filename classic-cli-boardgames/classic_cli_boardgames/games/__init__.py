"""Game modules and shared game interfaces."""

from classic_cli_boardgames.core.interfaces import (
    GameEngine,
    GameOutcome,
    TerminalStatus,
)

__all__ = ["GameEngine", "GameOutcome", "TerminalStatus"]
