"""Randomness helpers shared across games and AI."""

from __future__ import annotations

import random
from typing import Optional


def create_rng(seed: Optional[int] = None) -> random.Random:
    """Create a Random instance, optionally seeded for determinism."""
    rng = random.Random()
    if seed is not None:
        rng.seed(seed)
    return rng
