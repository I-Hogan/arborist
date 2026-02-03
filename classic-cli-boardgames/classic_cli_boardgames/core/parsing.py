"""Input parsing helpers shared across CLI and game modules."""

from __future__ import annotations

import shlex
from typing import Iterable, Optional, Sequence


def normalize_text(text: str) -> str:
    """Normalize user input for consistent comparisons."""
    return text.strip().lower()


def split_tokens(text: str) -> list[str]:
    """Split a raw input string into tokens, respecting simple quotes."""
    cleaned = text.strip()
    if not cleaned:
        return []
    try:
        return shlex.split(cleaned)
    except ValueError:
        return cleaned.split()


def parse_int(text: str) -> Optional[int]:
    """Parse an integer from text, returning None if it is invalid."""
    cleaned = text.strip()
    if not cleaned:
        return None
    try:
        return int(cleaned, 10)
    except ValueError:
        return None


def parse_int_in_range(text: str, minimum: int, maximum: int) -> Optional[int]:
    """Parse an integer and ensure it falls within the provided bounds."""
    value = parse_int(text)
    if value is None:
        return None
    if value < minimum or value > maximum:
        return None
    return value


def parse_choice(
    text: str, choices: Sequence[str], *, normalize: bool = True
) -> Optional[str]:
    """Return the matching choice from a list of choices."""
    cleaned = text.strip()
    if not cleaned:
        return None
    if normalize:
        cleaned = normalize_text(cleaned)
        for choice in choices:
            if cleaned == normalize_text(choice):
                return choice
        return None
    for choice in choices:
        if cleaned == choice:
            return choice
    return None


def parse_alias(text: str, aliases: Iterable[tuple[str, ...]]) -> Optional[int]:
    """Return the index of the first alias group that matches the input."""
    cleaned = normalize_text(text)
    if not cleaned:
        return None
    for index, group in enumerate(aliases):
        for alias in group:
            if cleaned == normalize_text(alias):
                return index
    return None
