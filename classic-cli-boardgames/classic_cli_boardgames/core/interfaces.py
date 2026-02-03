"""Shared game and AI interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, Sequence, TypeVar, runtime_checkable

StateT = TypeVar("StateT")
MoveT = TypeVar("MoveT")


@dataclass(frozen=True)
class GameOutcome:
    """Summary of a finished game."""

    winner: Optional[str]
    reason: str


@dataclass(frozen=True)
class TerminalStatus:
    """Terminal state metadata for a game."""

    is_terminal: bool
    outcome: Optional[GameOutcome] = None


@runtime_checkable
class GameEngine(Protocol[StateT, MoveT]):
    """Interface for game rule engines."""

    name: str

    def new_game(self) -> StateT:
        """Create and return an initial game state."""
        ...

    def legal_moves(self, state: StateT) -> Sequence[MoveT]:
        """Return the legal moves for the current state."""
        ...

    def apply_move(self, state: StateT, move: MoveT) -> StateT:
        """Apply a move and return the resulting state."""
        ...

    def is_terminal(self, state: StateT) -> TerminalStatus:
        """Return terminal metadata for the current state."""
        ...

    def render(self, state: StateT) -> str:
        """Render the current state for CLI display."""
        ...


@dataclass(frozen=True)
class AIDifficulty:
    """AI difficulty settings shared across games."""

    name: str
    max_depth: int
    time_limit_seconds: Optional[float] = None
    max_nodes: Optional[int] = None


@dataclass(frozen=True)
class AIConfig:
    """AI configuration including determinism controls."""

    difficulty: AIDifficulty
    seed: Optional[int] = None


@runtime_checkable
class AIEngine(Protocol[StateT, MoveT]):
    """Interface for AI move selection."""

    name: str

    def choose_move(
        self,
        state: StateT,
        legal_moves: Sequence[MoveT],
        config: AIConfig,
    ) -> MoveT:
        """Select a move from the available legal moves."""
        ...
