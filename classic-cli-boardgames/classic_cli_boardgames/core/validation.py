"""Validation helpers shared across games."""

from __future__ import annotations

from typing import Sequence, TypeVar

T = TypeVar("T")


def _validate_bounds(minimum: int, maximum: int) -> None:
    if minimum > maximum:
        raise ValueError("minimum must be less than or equal to maximum")


def clamp_int(value: int, minimum: int, maximum: int) -> int:
    """Clamp an integer between a minimum and maximum value."""
    _validate_bounds(minimum, maximum)
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def require_in_range(
    value: int, minimum: int, maximum: int, *, name: str = "value"
) -> int:
    """Ensure an integer falls within the provided bounds."""
    _validate_bounds(minimum, maximum)
    if value < minimum or value > maximum:
        raise ValueError(f"{name} must be between {minimum} and {maximum}")
    return value


def require_non_empty(text: str, *, name: str = "value") -> str:
    """Ensure the provided text is not empty after stripping."""
    cleaned = text.strip()
    if not cleaned:
        raise ValueError(f"{name} must not be empty")
    return cleaned


def require_rectangular_grid(grid: Sequence[Sequence[T]]) -> tuple[int, int]:
    """Ensure the grid is rectangular and return (rows, columns)."""
    if not grid:
        raise ValueError("grid must not be empty")
    columns = len(grid[0])
    if columns == 0:
        raise ValueError("grid must contain at least one column")
    for row in grid:
        if len(row) != columns:
            raise ValueError("grid rows must be the same length")
    return len(grid), columns
