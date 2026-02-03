"""Shared search helpers for game AIs."""

from __future__ import annotations

from dataclasses import dataclass, field
import time

from classic_cli_boardgames.core.interfaces import AIDifficulty


@dataclass
class SearchContext:
    """Track search limits across a move selection."""

    difficulty: AIDifficulty
    start_time: float = field(default_factory=time.monotonic)
    nodes: int = 0

    def out_of_budget(self) -> bool:
        """Return True when the search should stop due to limits."""
        if (
            self.difficulty.max_nodes is not None
            and self.nodes >= self.difficulty.max_nodes
        ):
            return True
        if self.difficulty.time_limit_seconds is None:
            return False
        elapsed = time.monotonic() - self.start_time
        return elapsed >= self.difficulty.time_limit_seconds
