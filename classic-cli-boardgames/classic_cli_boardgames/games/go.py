"""Go rules, move generation, and rendering (9x9, area scoring)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable, Optional, Sequence

from classic_cli_boardgames.core.interfaces import GameOutcome, TerminalStatus
from classic_cli_boardgames.core.rendering import render_grid

BOARD_SIZE = 9
COL_LABELS = ("A", "B", "C", "D", "E", "F", "G", "H", "J")
ROW_LABELS = tuple(str(rank) for rank in range(BOARD_SIZE, 0, -1))


class Color(str, Enum):
    BLACK = "black"
    WHITE = "white"

    def opponent(self) -> "Color":
        return Color.WHITE if self is Color.BLACK else Color.BLACK

    @property
    def label(self) -> str:
        return "Black" if self is Color.BLACK else "White"


_STONE_SYMBOLS = {Color.BLACK: "B", Color.WHITE: "W"}


@dataclass(frozen=True)
class Stone:
    color: Color

    def symbol(self) -> str:
        return _STONE_SYMBOLS[self.color]


Position = tuple[int, int]
Board = tuple[tuple[Optional[Stone], ...], ...]


@dataclass(frozen=True)
class Move:
    position: Optional[Position] = None

    @property
    def is_pass(self) -> bool:
        return self.position is None

    def notation(self) -> str:
        if self.is_pass:
            return "pass"
        return position_to_coordinate(self.position)


@dataclass(frozen=True)
class GoState:
    board: Board
    active_color: Color
    previous_board: Optional[Board]
    consecutive_passes: int
    captures_black: int
    captures_white: int


class GoEngine:
    """Go rules engine (9x9, simple ko, area scoring)."""

    name = "Go"

    def new_game(self) -> GoState:
        board = tuple(tuple(None for _ in range(BOARD_SIZE)) for _ in range(BOARD_SIZE))
        return GoState(
            board=board,
            active_color=Color.BLACK,
            previous_board=None,
            consecutive_passes=0,
            captures_black=0,
            captures_white=0,
        )

    def legal_moves(self, state: GoState) -> Sequence[Move]:
        moves: list[Move] = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if state.board[row][col] is not None:
                    continue
                candidate = (row, col)
                result = _place_stone(state.board, state.active_color, candidate)
                if result is None:
                    continue
                new_board, _ = result
                if (
                    state.previous_board is not None
                    and new_board == state.previous_board
                ):
                    continue
                moves.append(Move(candidate))
        moves.append(Move())
        return moves

    def apply_move(self, state: GoState, move: Move) -> GoState:
        if move.is_pass:
            return GoState(
                board=state.board,
                active_color=state.active_color.opponent(),
                previous_board=state.board,
                consecutive_passes=state.consecutive_passes + 1,
                captures_black=state.captures_black,
                captures_white=state.captures_white,
            )

        if move.position is None:
            raise ValueError("Move must include a position")
        row, col = move.position
        if not _in_bounds(row, col):
            raise ValueError("Move out of bounds")
        if state.board[row][col] is not None:
            raise ValueError("Position already occupied")

        result = _place_stone(state.board, state.active_color, (row, col))
        if result is None:
            raise ValueError("Illegal move")
        new_board, captured = result
        if state.previous_board is not None and new_board == state.previous_board:
            raise ValueError("Move violates ko")

        captures_black = state.captures_black
        captures_white = state.captures_white
        if state.active_color is Color.BLACK:
            captures_black += captured
        else:
            captures_white += captured

        return GoState(
            board=new_board,
            active_color=state.active_color.opponent(),
            previous_board=state.board,
            consecutive_passes=0,
            captures_black=captures_black,
            captures_white=captures_white,
        )

    def is_terminal(self, state: GoState) -> TerminalStatus:
        if state.consecutive_passes < 2:
            return TerminalStatus(False, None)
        black_score, white_score = compute_area_score(state.board)
        if black_score > white_score:
            winner = Color.BLACK.label
        elif white_score > black_score:
            winner = Color.WHITE.label
        else:
            winner = None
        reason = f"area score {black_score}-{white_score}"
        return TerminalStatus(True, GameOutcome(winner, reason))

    def render(self, state: GoState) -> str:
        return render_state(state)


def position_to_coordinate(position: Position) -> str:
    row, col = position
    return f"{COL_LABELS[col]}{BOARD_SIZE - row}"


def coordinate_to_position(coord: str) -> Optional[Position]:
    text = coord.strip().upper()
    if len(text) < 2:
        return None
    col_letter = text[0]
    if col_letter not in COL_LABELS:
        return None
    try:
        number = int(text[1:])
    except ValueError:
        return None
    if number < 1 or number > BOARD_SIZE:
        return None
    col = COL_LABELS.index(col_letter)
    row = BOARD_SIZE - number
    return row, col


_COORDINATE_RE = re.compile(r"[A-HJ][1-9](?!\d)", re.IGNORECASE)


def parse_move_input(
    text: str, legal_moves: Sequence[Move]
) -> tuple[Optional[Move], Optional[str]]:
    cleaned = text.strip().lower()
    if cleaned in {"pass", "p"}:
        for move in legal_moves:
            if move.is_pass:
                return move, None
        return None, "Passing is not available right now."

    matches = _COORDINATE_RE.findall(text)
    if len(matches) != 1:
        return None, "Enter a move like D4 or pass."
    position = coordinate_to_position(matches[0])
    if position is None:
        return None, "Use coordinates from A1 to J9 (skipping I)."

    for move in legal_moves:
        if move.position == position:
            return move, None
    return None, "That move is not legal."


def render_state(state: GoState) -> str:
    grid: list[list[str]] = []
    for row in state.board:
        rendered_row = []
        for stone in row:
            rendered_row.append(stone.symbol() if stone is not None else ".")
        grid.append(rendered_row)
    board = render_grid(
        grid,
        row_labels=ROW_LABELS,
        col_labels=COL_LABELS,
        cell_width=1,
        padding=1,
    )
    lines = [
        f"Turn: {state.active_color.label}",
        f"Captures: Black {state.captures_black} | White {state.captures_white}",
        f"Consecutive passes: {state.consecutive_passes}",
        board,
    ]
    return "\n".join(lines)


def compute_area_score(board: Board) -> tuple[int, int]:
    black_stones = 0
    white_stones = 0
    for row in board:
        for stone in row:
            if stone is None:
                continue
            if stone.color is Color.BLACK:
                black_stones += 1
            else:
                white_stones += 1

    visited: set[Position] = set()
    black_territory = 0
    white_territory = 0
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] is not None or (row, col) in visited:
                continue
            region, colors = _collect_region(board, (row, col))
            visited.update(region)
            if len(colors) == 1:
                color = next(iter(colors))
                if color is Color.BLACK:
                    black_territory += len(region)
                else:
                    white_territory += len(region)

    return black_stones + black_territory, white_stones + white_territory


def iter_groups(board: Board) -> Iterable[tuple[Color, set[Position], set[Position]]]:
    visited: set[Position] = set()
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if (row, col) in visited:
                continue
            stone = board[row][col]
            if stone is None:
                continue
            group, liberties = _collect_group(board, (row, col))
            visited.update(group)
            yield stone.color, group, liberties


def _place_stone(
    board: Board, color: Color, position: Position
) -> Optional[tuple[Board, int]]:
    row, col = position
    if board[row][col] is not None:
        return None
    working = [list(row_cells) for row_cells in board]
    working[row][col] = Stone(color)
    opponent = color.opponent()
    captured: set[Position] = set()
    for neighbor in _neighbors(position):
        stone = working[neighbor[0]][neighbor[1]]
        if stone is None or stone.color is not opponent:
            continue
        group, liberties = _collect_group(working, neighbor)
        if not liberties:
            captured.update(group)

    for captured_pos in captured:
        working[captured_pos[0]][captured_pos[1]] = None

    group, liberties = _collect_group(working, position)
    if not liberties:
        return None
    new_board = tuple(tuple(row_cells) for row_cells in working)
    return new_board, len(captured)


def _collect_region(board: Board, start: Position) -> tuple[set[Position], set[Color]]:
    stack = [start]
    region: set[Position] = set()
    bordering_colors: set[Color] = set()
    while stack:
        row, col = stack.pop()
        if (row, col) in region:
            continue
        region.add((row, col))
        for neighbor in _neighbors((row, col)):
            stone = board[neighbor[0]][neighbor[1]]
            if stone is None:
                if neighbor not in region:
                    stack.append(neighbor)
            else:
                bordering_colors.add(stone.color)
    return region, bordering_colors


def _collect_group(
    board: Sequence[Sequence[Optional[Stone]]], start: Position
) -> tuple[set[Position], set[Position]]:
    start_stone = board[start[0]][start[1]]
    if start_stone is None:
        return set(), set()
    color = start_stone.color
    stack = [start]
    group: set[Position] = set()
    liberties: set[Position] = set()
    while stack:
        row, col = stack.pop()
        if (row, col) in group:
            continue
        group.add((row, col))
        for neighbor in _neighbors((row, col)):
            stone = board[neighbor[0]][neighbor[1]]
            if stone is None:
                liberties.add(neighbor)
            elif stone.color is color and neighbor not in group:
                stack.append(neighbor)
    return group, liberties


def _neighbors(position: Position) -> list[Position]:
    row, col = position
    neighbors: list[Position] = []
    if row > 0:
        neighbors.append((row - 1, col))
    if row < BOARD_SIZE - 1:
        neighbors.append((row + 1, col))
    if col > 0:
        neighbors.append((row, col - 1))
    if col < BOARD_SIZE - 1:
        neighbors.append((row, col + 1))
    return neighbors


def _in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE
