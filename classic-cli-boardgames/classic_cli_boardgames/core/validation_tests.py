import pytest

from classic_cli_boardgames.core.validation import (
    clamp_int,
    require_in_range,
    require_non_empty,
    require_rectangular_grid,
)


def test_clamp_int_bounds() -> None:
    assert clamp_int(0, 1, 3) == 1
    assert clamp_int(2, 1, 3) == 2
    assert clamp_int(5, 1, 3) == 3


def test_clamp_int_invalid_range() -> None:
    with pytest.raises(
        ValueError, match="minimum must be less than or equal to maximum"
    ):
        clamp_int(1, 3, 1)


def test_require_in_range() -> None:
    assert require_in_range(2, 1, 3) == 2
    with pytest.raises(ValueError, match="value must be between 1 and 3"):
        require_in_range(5, 1, 3)


def test_require_non_empty() -> None:
    assert require_non_empty("  ok  ") == "ok"
    with pytest.raises(ValueError, match="name must not be empty"):
        require_non_empty("   ", name="name")


def test_require_rectangular_grid() -> None:
    assert require_rectangular_grid(((1, 2), (3, 4))) == (2, 2)
    with pytest.raises(ValueError, match="grid must not be empty"):
        require_rectangular_grid(())
    with pytest.raises(ValueError, match="grid rows must be the same length"):
        require_rectangular_grid(((1,), (1, 2)))
