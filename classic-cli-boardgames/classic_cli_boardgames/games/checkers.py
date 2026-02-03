"""Checkers rules, move generation, and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Optional, Sequence

from classic_cli_boardgames.core.interfaces import GameOutcome, TerminalStatus
from classic_cli_boardgames.core.rendering import alphabetic_labels, render_grid


class Color(str, Enum):
    WHITE = "white"
    BLACK = "black"

    def opponent(self) -> "Color":
        return Color.BLACK if self is Color.WHITE else Color.WHITE

    @property
    def label(self) -> str:
        return "White" if self is Color.WHITE else "Black"


class PieceType(str, Enum):
    MAN = "man"
    KING = "king"


_PIECE_SYMBOLS = {
    (Color.WHITE, PieceType.MAN): "w",
    (Color.WHITE, PieceType.KING): "W",
    (Color.BLACK, PieceType.MAN): "b",
    (Color.BLACK, PieceType.KING): "B",
}


@dataclass(frozen=True)
class Piece:
    color: Color
    kind: PieceType

    def symbol(self) -> str:
        return _PIECE_SYMBOLS[(self.color, self.kind)]


Position = tuple[int, int]


@dataclass(frozen=True)
class Move:
    path: tuple[Position, ...]
    captures: tuple[Position, ...] = ()

    @property
    def is_capture(self) -> bool:
        return bool(self.captures)

    def notation(self) -> str:
        coordinates = [position_to_algebraic(pos) for pos in self.path]
        separator = "x" if self.is_capture else "-"
        return separator.join(coordinates)


@dataclass(frozen=True)
class CheckersState:
    board: tuple[tuple[Optional[Piece], ...], ...]
    active_color: Color


class CheckersEngine:
    """Checkers rules engine."""

    name = "Checkers"

    def new_game(self) -> CheckersState:
        return CheckersState(board=_initial_board(), active_color=Color.BLACK)

    def legal_moves(self, state: CheckersState) -> Sequence[Move]:
        return _legal_moves(state)

    def apply_move(self, state: CheckersState, move: Move) -> CheckersState:
        return _apply_move(state, move)

    def is_terminal(self, state: CheckersState) -> TerminalStatus:
        moves = _legal_moves(state)
        if moves:
            return TerminalStatus(False, None)
        winner = state.active_color.opponent().label
        return TerminalStatus(True, GameOutcome(winner, "no moves"))

    def render(self, state: CheckersState) -> str:
        return render_state(state)


FILES = "abcdefgh"
RANKS = "12345678"


def position_to_algebraic(position: Position) -> str:
    row, col = position
    file = FILES[col]
    rank = RANKS[7 - row]
    return f"{file}{rank}"


def algebraic_to_position(coord: str) -> Optional[Position]:
    if len(coord) != 2:
        return None
    file = coord[0].lower()
    rank = coord[1]
    if file not in FILES or rank not in RANKS:
        return None
    col = FILES.index(file)
    row = 7 - RANKS.index(rank)
    return row, col


def render_state(state: CheckersState) -> str:
    grid: list[list[str]] = []
    for row_index, row in enumerate(state.board):
        rendered_row: list[str] = []
        for col_index, piece in enumerate(row):
            if piece is None:
                rendered_row.append(
                    "." if _is_dark_square(row_index, col_index) else " "
                )
            else:
                rendered_row.append(piece.symbol())
        grid.append(rendered_row)
    row_labels = [str(rank) for rank in range(8, 0, -1)]
    col_labels = alphabetic_labels(8, uppercase=True)
    board = render_grid(
        grid, row_labels=row_labels, col_labels=col_labels, cell_width=1, padding=1
    )
    lines = [f"Turn: {state.active_color.label}", board]
    if any(move.is_capture for move in _legal_moves(state)):
        lines.append("Captures available.")
    return "\n".join(lines)


_COORDINATE_RE = re.compile(r"[a-hA-H][1-8]")


def parse_move_input(
    text: str, legal_moves: Sequence[Move]
) -> tuple[Optional[Move], Optional[str]]:
    coordinates = _COORDINATE_RE.findall(text)
    if len(coordinates) < 2:
        return None, "Enter a move like b6-a5 or b6-d4-f2."

    positions: list[Position] = []
    for coord in coordinates:
        position = algebraic_to_position(coord)
        if position is None:
            return None, "Use coordinates between a1 and h8."
        positions.append(position)

    if len(positions) == 2:
        start, end = positions
        matches = [
            move
            for move in legal_moves
            if move.path[0] == start and move.path[-1] == end
        ]
        if len(matches) == 1:
            return matches[0], None
        if len(matches) > 1:
            return None, "Multiple capture paths match that move. Enter the full path."
    else:
        matches = [move for move in legal_moves if move.path == tuple(positions)]
        if matches:
            return matches[0], None

    if any(move.is_capture for move in legal_moves):
        if _looks_like_simple_move(positions):
            return None, "Captures are required when available."

    return None, "That move is not legal."


def _looks_like_simple_move(positions: Sequence[Position]) -> bool:
    if len(positions) != 2:
        return False
    start, end = positions
    return abs(end[0] - start[0]) == 1 and abs(end[1] - start[1]) == 1


def _initial_board() -> tuple[tuple[Optional[Piece], ...], ...]:
    board: list[list[Optional[Piece]]] = []
    for row in range(8):
        row_cells: list[Optional[Piece]] = []
        for col in range(8):
            if not _is_dark_square(row, col):
                row_cells.append(None)
                continue
            if row < 3:
                row_cells.append(Piece(Color.BLACK, PieceType.MAN))
            elif row > 4:
                row_cells.append(Piece(Color.WHITE, PieceType.MAN))
            else:
                row_cells.append(None)
        board.append(row_cells)
    return tuple(tuple(row) for row in board)


def _legal_moves(state: CheckersState) -> Sequence[Move]:
    capture_moves: list[Move] = []
    for position, piece in _iter_pieces(state.board, state.active_color):
        capture_moves.extend(_capture_moves_for_piece(state.board, position, piece))
    if capture_moves:
        return capture_moves

    simple_moves: list[Move] = []
    for position, piece in _iter_pieces(state.board, state.active_color):
        simple_moves.extend(_simple_moves_for_piece(state.board, position, piece))
    return simple_moves


def _apply_move(state: CheckersState, move: Move) -> CheckersState:
    board = [list(row) for row in state.board]
    start = move.path[0]
    end = move.path[-1]
    piece = board[start[0]][start[1]]
    if piece is None:
        raise ValueError("no piece on move start")
    board[start[0]][start[1]] = None
    for captured in move.captures:
        board[captured[0]][captured[1]] = None
    if piece.kind is PieceType.MAN and _is_king_row(piece.color, end[0]):
        piece = Piece(piece.color, PieceType.KING)
    board[end[0]][end[1]] = piece
    return CheckersState(
        board=tuple(tuple(row) for row in board),
        active_color=state.active_color.opponent(),
    )


def _iter_pieces(board: Sequence[Sequence[Optional[Piece]]], color: Color):
    for row_index, row in enumerate(board):
        for col_index, piece in enumerate(row):
            if piece is not None and piece.color is color:
                yield (row_index, col_index), piece


def _simple_moves_for_piece(
    board: Sequence[Sequence[Optional[Piece]]],
    position: Position,
    piece: Piece,
) -> list[Move]:
    moves: list[Move] = []
    row, col = position
    for row_delta, col_delta in _move_directions(piece):
        next_row = row + row_delta
        next_col = col + col_delta
        if not _in_bounds(next_row, next_col):
            continue
        if board[next_row][next_col] is None:
            moves.append(Move((position, (next_row, next_col))))
    return moves


def _capture_moves_for_piece(
    board: Sequence[Sequence[Optional[Piece]]],
    position: Position,
    piece: Piece,
) -> list[Move]:
    board_copy = [list(row) for row in board]
    return _capture_sequences(
        board_copy, position, piece, path=(position,), captured=()
    )


def _capture_sequences(
    board: list[list[Optional[Piece]]],
    position: Position,
    piece: Piece,
    *,
    path: tuple[Position, ...],
    captured: tuple[Position, ...],
) -> list[Move]:
    sequences: list[Move] = []
    row, col = position
    found_jump = False

    for row_delta, col_delta in _capture_directions(piece):
        mid_row = row + row_delta // 2
        mid_col = col + col_delta // 2
        dest_row = row + row_delta
        dest_col = col + col_delta
        if not (_in_bounds(mid_row, mid_col) and _in_bounds(dest_row, dest_col)):
            continue
        mid_piece = board[mid_row][mid_col]
        if mid_piece is None or mid_piece.color is piece.color:
            continue
        if board[dest_row][dest_col] is not None:
            continue

        found_jump = True
        new_board = [board_row.copy() for board_row in board]
        new_board[row][col] = None
        new_board[mid_row][mid_col] = None
        new_board[dest_row][dest_col] = piece

        new_path = path + ((dest_row, dest_col),)
        new_captured = captured + ((mid_row, mid_col),)

        if piece.kind is PieceType.MAN and _is_king_row(piece.color, dest_row):
            sequences.append(Move(new_path, new_captured))
            continue

        sequences.extend(
            _capture_sequences(
                new_board,
                (dest_row, dest_col),
                piece,
                path=new_path,
                captured=new_captured,
            )
        )

    if not found_jump and captured:
        sequences.append(Move(path, captured))

    return sequences


def _move_directions(piece: Piece) -> tuple[tuple[int, int], ...]:
    if piece.kind is PieceType.KING:
        return ((-1, -1), (-1, 1), (1, -1), (1, 1))
    direction = -1 if piece.color is Color.WHITE else 1
    return ((direction, -1), (direction, 1))


def _capture_directions(piece: Piece) -> tuple[tuple[int, int], ...]:
    if piece.kind is PieceType.KING:
        return ((-2, -2), (-2, 2), (2, -2), (2, 2))
    direction = -2 if piece.color is Color.WHITE else 2
    return ((direction, -2), (direction, 2))


def _is_dark_square(row: int, col: int) -> bool:
    return (row + col) % 2 == 1


def _is_king_row(color: Color, row: int) -> bool:
    return row == 0 if color is Color.WHITE else row == 7


def _in_bounds(row: int, col: int) -> bool:
    return 0 <= row < 8 and 0 <= col < 8
