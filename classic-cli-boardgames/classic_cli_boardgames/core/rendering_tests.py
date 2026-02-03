import pytest

from classic_cli_boardgames.core.rendering import (
    alphabetic_labels,
    numeric_labels,
    render_grid,
)


def test_label_helpers() -> None:
    assert alphabetic_labels(3) == ["A", "B", "C"]
    assert alphabetic_labels(2, uppercase=False) == ["a", "b"]
    assert numeric_labels(3, start=0) == ["0", "1", "2"]


def test_render_grid_with_labels() -> None:
    grid = (("X", "O"), ("O", "X"))
    rendered = render_grid(grid, row_labels=("1", "2"), col_labels=("A", "B"))
    expected = "\n".join(
        [
            "  | A | B |",
            "  +---+---+",
            "1 | X | O |",
            "  +---+---+",
            "2 | O | X |",
            "  +---+---+",
        ]
    )
    assert rendered == expected


def test_render_grid_label_mismatch() -> None:
    grid = (("X", "O"), ("O", "X"))
    with pytest.raises(ValueError, match="row labels must have length 2"):
        render_grid(grid, row_labels=("1",))
    with pytest.raises(ValueError, match="column labels must have length 2"):
        render_grid(grid, col_labels=("A",))
