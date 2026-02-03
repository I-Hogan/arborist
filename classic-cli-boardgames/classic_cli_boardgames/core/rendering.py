"""Board rendering helpers for CLI display."""

from __future__ import annotations

import string
from typing import Iterable, Sequence, TypeVar

from classic_cli_boardgames.core.validation import require_rectangular_grid

CellT = TypeVar("CellT")


def alphabetic_labels(count: int, *, uppercase: bool = True) -> list[str]:
    """Return Excel-style alphabetic labels (A, B, ..., Z, AA, AB, ...)."""
    if count < 0:
        raise ValueError("count must be non-negative")
    if count == 0:
        return []
    alphabet = string.ascii_uppercase if uppercase else string.ascii_lowercase

    def label_for(index: int) -> str:
        result = ""
        while index > 0:
            index, remainder = divmod(index - 1, 26)
            result = alphabet[remainder] + result
        return result

    return [label_for(i + 1) for i in range(count)]


def numeric_labels(count: int, *, start: int = 1) -> list[str]:
    """Return numeric labels as strings."""
    if count < 0:
        raise ValueError("count must be non-negative")
    return [str(start + offset) for offset in range(count)]


def _normalize_labels(
    labels: Iterable[str] | None, expected: int, label_name: str
) -> list[str] | None:
    if labels is None:
        return None
    labels_list = [str(label) for label in labels]
    if len(labels_list) != expected:
        raise ValueError(f"{label_name} labels must have length {expected}")
    return labels_list


def render_grid(
    grid: Sequence[Sequence[CellT]],
    *,
    row_labels: Iterable[str] | None = None,
    col_labels: Iterable[str] | None = None,
    cell_width: int | None = None,
    padding: int = 1,
    border: bool = True,
) -> str:
    """Render a rectangular grid with optional row/column labels."""
    if padding < 0:
        raise ValueError("padding must be non-negative")
    rows, columns = require_rectangular_grid(grid)
    cell_strings = [[str(cell) for cell in row] for row in grid]
    row_label_list = _normalize_labels(row_labels, rows, "row")
    col_label_list = _normalize_labels(col_labels, columns, "column")

    max_cell_length = max(len(cell) for row in cell_strings for cell in row)
    label_length = max((len(label) for label in col_label_list or ()), default=0)
    min_width = max(max_cell_length, label_length, 1)

    if cell_width is None:
        content_width = min_width
    else:
        if cell_width < 1:
            raise ValueError("cell_width must be at least 1")
        if cell_width < min_width:
            raise ValueError("cell_width is too small for cell contents")
        content_width = cell_width

    cell_total_width = content_width + padding * 2
    row_label_width = max((len(label) for label in row_label_list or ()), default=0)

    def format_cell(text: str) -> str:
        return " " * padding + text.center(content_width) + " " * padding

    def render_line(cells: Sequence[str], row_label: str | None) -> str:
        rendered_cells = [format_cell(cell) for cell in cells]
        line = (
            "|" + "|".join(rendered_cells) + "|" if border else " ".join(rendered_cells)
        )
        if row_label is None:
            return line
        return f"{row_label:>{row_label_width}} {line}"

    lines: list[str] = []
    if col_label_list is not None:
        lines.append(
            render_line(col_label_list, "" if row_label_list is not None else None)
        )

    if border:
        separator = "+" + "+".join("-" * cell_total_width for _ in range(columns)) + "+"
        if row_label_list is not None:
            lines.append(" " * (row_label_width + 1) + separator)
        else:
            lines.append(separator)

    for row_index, row in enumerate(cell_strings):
        label = row_label_list[row_index] if row_label_list is not None else None
        lines.append(render_line(row, label))
        if border:
            if row_label_list is not None:
                lines.append(" " * (row_label_width + 1) + separator)
            else:
                lines.append(separator)

    return "\n".join(lines)
