"""Chess rules, move generation, and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Sequence

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
    PAWN = "pawn"
    KNIGHT = "knight"
    BISHOP = "bishop"
    ROOK = "rook"
    QUEEN = "queen"
    KING = "king"


_PIECE_SYMBOLS = {
    (Color.WHITE, PieceType.PAWN): "P",
    (Color.WHITE, PieceType.KNIGHT): "N",
    (Color.WHITE, PieceType.BISHOP): "B",
    (Color.WHITE, PieceType.ROOK): "R",
    (Color.WHITE, PieceType.QUEEN): "Q",
    (Color.WHITE, PieceType.KING): "K",
    (Color.BLACK, PieceType.PAWN): "p",
    (Color.BLACK, PieceType.KNIGHT): "n",
    (Color.BLACK, PieceType.BISHOP): "b",
    (Color.BLACK, PieceType.ROOK): "r",
    (Color.BLACK, PieceType.QUEEN): "q",
    (Color.BLACK, PieceType.KING): "k",
}


@dataclass(frozen=True)
class Piece:
    color: Color
    kind: PieceType

    def symbol(self) -> str:
        return _PIECE_SYMBOLS[(self.color, self.kind)]


Position = tuple[int, int]


@dataclass(frozen=True)
class CastlingRights:
    white_kingside: bool = True
    white_queenside: bool = True
    black_kingside: bool = True
    black_queenside: bool = True


@dataclass(frozen=True)
class Move:
    start: Position
    end: Position
    promotion: Optional[PieceType] = None
    is_castling: bool = False
    is_en_passant: bool = False

    def notation(self) -> str:
        start = position_to_algebraic(self.start)
        end = position_to_algebraic(self.end)
        if self.promotion is None:
            return f"{start}{end}"
        return f"{start}{end}{_promotion_letter(self.promotion)}"


@dataclass(frozen=True)
class ChessState:
    board: tuple[tuple[Optional[Piece], ...], ...]
    active_color: Color
    castling_rights: CastlingRights
    en_passant_target: Optional[Position] = None
    halfmove_clock: int = 0
    fullmove: int = 1


class ChessEngine:
    """Chess rules engine."""

    name = "Chess"

    def new_game(self) -> ChessState:
        return ChessState(
            board=_initial_board(),
            active_color=Color.WHITE,
            castling_rights=CastlingRights(),
            en_passant_target=None,
            halfmove_clock=0,
            fullmove=1,
        )

    def legal_moves(self, state: ChessState) -> Sequence[Move]:
        return _legal_moves(state)

    def apply_move(self, state: ChessState, move: Move) -> ChessState:
        return _apply_move(state, move)

    def is_terminal(self, state: ChessState) -> TerminalStatus:
        moves = _legal_moves(state)
        if moves:
            return TerminalStatus(False, None)
        if _is_in_check(state, state.active_color):
            winner = state.active_color.opponent().label
            return TerminalStatus(True, GameOutcome(winner, "checkmate"))
        return TerminalStatus(True, GameOutcome(None, "stalemate"))

    def render(self, state: ChessState) -> str:
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


def render_state(state: ChessState) -> str:
    grid = []
    for row in state.board:
        grid.append([piece.symbol() if piece else "." for piece in row])
    row_labels = [str(rank) for rank in range(8, 0, -1)]
    col_labels = alphabetic_labels(8, uppercase=True)
    board = render_grid(
        grid, row_labels=row_labels, col_labels=col_labels, cell_width=1, padding=1
    )
    lines = [f"Turn: {state.active_color.label}", board]
    if _is_in_check(state, state.active_color):
        lines.append(f"{state.active_color.label} is in check.")
    return "\n".join(lines)


def parse_move_input(
    text: str, legal_moves: Sequence[Move]
) -> tuple[Optional[Move], Optional[str]]:
    cleaned = "".join(text.strip().lower().split())
    if not cleaned:
        return None, "Enter a move such as e2e4 or e7e8q."

    castle_move = _parse_castling(cleaned, legal_moves)
    if castle_move is not None:
        return castle_move, None

    compact = cleaned.replace("-", "")
    if len(compact) not in (4, 5):
        return None, "Moves must be in the form e2e4 or e7e8q."

    start = algebraic_to_position(compact[:2])
    end = algebraic_to_position(compact[2:4])
    if start is None or end is None:
        return None, "Use coordinates between a1 and h8."

    promotion = None
    if len(compact) == 5:
        promotion = _promotion_from_letter(compact[4])
        if promotion is None:
            return None, "Promotion must be one of q, r, b, n."

    matches = [
        move for move in legal_moves if _matches_move(move, start, end, promotion)
    ]
    if matches:
        return matches[0], None

    if promotion is None:
        promo_moves = [
            move
            for move in legal_moves
            if move.start == start and move.end == end and move.promotion is not None
        ]
        if promo_moves:
            return None, "Promotion required. Add q, r, b, or n (e.g., e7e8q)."

    return None, "That move is not legal."


def _parse_castling(text: str, legal_moves: Sequence[Move]) -> Optional[Move]:
    castles = {
        "o-o": 6,
        "0-0": 6,
        "o-o-o": 2,
        "0-0-0": 2,
    }
    if text not in castles:
        return None
    target_col = castles[text]
    for move in legal_moves:
        if move.is_castling and move.end[1] == target_col:
            return move
    return None


def _promotion_from_letter(letter: str) -> Optional[PieceType]:
    mapping = {
        "q": PieceType.QUEEN,
        "r": PieceType.ROOK,
        "b": PieceType.BISHOP,
        "n": PieceType.KNIGHT,
    }
    return mapping.get(letter)


def _promotion_letter(piece: PieceType) -> str:
    letters = {
        PieceType.QUEEN: "q",
        PieceType.ROOK: "r",
        PieceType.BISHOP: "b",
        PieceType.KNIGHT: "n",
    }
    return letters[piece]


def _matches_move(
    move: Move, start: Position, end: Position, promotion: Optional[PieceType]
) -> bool:
    if move.start != start or move.end != end:
        return False
    if promotion is None:
        return move.promotion is None
    return move.promotion == promotion


def _initial_board() -> tuple[tuple[Optional[Piece], ...], ...]:
    black_back = (
        Piece(Color.BLACK, PieceType.ROOK),
        Piece(Color.BLACK, PieceType.KNIGHT),
        Piece(Color.BLACK, PieceType.BISHOP),
        Piece(Color.BLACK, PieceType.QUEEN),
        Piece(Color.BLACK, PieceType.KING),
        Piece(Color.BLACK, PieceType.BISHOP),
        Piece(Color.BLACK, PieceType.KNIGHT),
        Piece(Color.BLACK, PieceType.ROOK),
    )
    white_back = (
        Piece(Color.WHITE, PieceType.ROOK),
        Piece(Color.WHITE, PieceType.KNIGHT),
        Piece(Color.WHITE, PieceType.BISHOP),
        Piece(Color.WHITE, PieceType.QUEEN),
        Piece(Color.WHITE, PieceType.KING),
        Piece(Color.WHITE, PieceType.BISHOP),
        Piece(Color.WHITE, PieceType.KNIGHT),
        Piece(Color.WHITE, PieceType.ROOK),
    )
    return (
        black_back,
        tuple(Piece(Color.BLACK, PieceType.PAWN) for _ in range(8)),
        tuple(None for _ in range(8)),
        tuple(None for _ in range(8)),
        tuple(None for _ in range(8)),
        tuple(None for _ in range(8)),
        tuple(Piece(Color.WHITE, PieceType.PAWN) for _ in range(8)),
        white_back,
    )


def _legal_moves(state: ChessState) -> list[Move]:
    candidates = _pseudo_legal_moves(state)
    legal: list[Move] = []
    for move in candidates:
        next_state = _apply_move(state, move)
        if not _is_in_check(next_state, state.active_color):
            legal.append(move)
    return legal


def _pseudo_legal_moves(state: ChessState) -> list[Move]:
    moves: list[Move] = []
    for row in range(8):
        for col in range(8):
            piece = state.board[row][col]
            if piece is None or piece.color != state.active_color:
                continue
            position = (row, col)
            if piece.kind is PieceType.PAWN:
                moves.extend(_pawn_moves(state, position, piece))
            elif piece.kind is PieceType.KNIGHT:
                moves.extend(_knight_moves(state, position, piece))
            elif piece.kind is PieceType.BISHOP:
                moves.extend(_slider_moves(state, position, piece, _BISHOP_DIRECTIONS))
            elif piece.kind is PieceType.ROOK:
                moves.extend(_slider_moves(state, position, piece, _ROOK_DIRECTIONS))
            elif piece.kind is PieceType.QUEEN:
                moves.extend(_slider_moves(state, position, piece, _QUEEN_DIRECTIONS))
            elif piece.kind is PieceType.KING:
                moves.extend(_king_moves(state, position, piece))
    return moves


def _pawn_moves(state: ChessState, position: Position, piece: Piece) -> list[Move]:
    moves: list[Move] = []
    row, col = position
    direction = -1 if piece.color is Color.WHITE else 1
    start_row = 6 if piece.color is Color.WHITE else 1
    promotion_row = 0 if piece.color is Color.WHITE else 7

    one_step = (row + direction, col)
    if _is_in_bounds(one_step) and _piece_at(state, one_step) is None:
        if one_step[0] == promotion_row:
            moves.extend(_promotion_moves(position, one_step))
        else:
            moves.append(Move(position, one_step))
        two_step = (row + 2 * direction, col)
        if (
            row == start_row
            and _is_in_bounds(two_step)
            and _piece_at(state, two_step) is None
        ):
            moves.append(Move(position, two_step))

    for dc in (-1, 1):
        target = (row + direction, col + dc)
        if not _is_in_bounds(target):
            continue
        target_piece = _piece_at(state, target)
        if target_piece is not None and target_piece.color is not piece.color:
            if target[0] == promotion_row:
                moves.extend(_promotion_moves(position, target))
            else:
                moves.append(Move(position, target))
        if state.en_passant_target == target:
            moves.append(Move(position, target, is_en_passant=True))

    return moves


def _promotion_moves(start: Position, end: Position) -> Iterable[Move]:
    for piece in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
        yield Move(start, end, promotion=piece)


_KNIGHT_OFFSETS = (
    (-2, -1),
    (-2, 1),
    (-1, -2),
    (-1, 2),
    (1, -2),
    (1, 2),
    (2, -1),
    (2, 1),
)


def _knight_moves(state: ChessState, position: Position, piece: Piece) -> list[Move]:
    moves: list[Move] = []
    row, col = position
    for dr, dc in _KNIGHT_OFFSETS:
        target = (row + dr, col + dc)
        if not _is_in_bounds(target):
            continue
        target_piece = _piece_at(state, target)
        if target_piece is None or target_piece.color is not piece.color:
            moves.append(Move(position, target))
    return moves


_BISHOP_DIRECTIONS = ((-1, -1), (-1, 1), (1, -1), (1, 1))
_ROOK_DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))
_QUEEN_DIRECTIONS = _BISHOP_DIRECTIONS + _ROOK_DIRECTIONS


def _slider_moves(
    state: ChessState,
    position: Position,
    piece: Piece,
    directions: Iterable[tuple[int, int]],
) -> list[Move]:
    moves: list[Move] = []
    row, col = position
    for dr, dc in directions:
        step = 1
        while True:
            target = (row + dr * step, col + dc * step)
            if not _is_in_bounds(target):
                break
            target_piece = _piece_at(state, target)
            if target_piece is None:
                moves.append(Move(position, target))
            else:
                if target_piece.color is not piece.color:
                    moves.append(Move(position, target))
                break
            step += 1
    return moves


def _king_moves(state: ChessState, position: Position, piece: Piece) -> list[Move]:
    moves: list[Move] = []
    row, col = position
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            target = (row + dr, col + dc)
            if not _is_in_bounds(target):
                continue
            target_piece = _piece_at(state, target)
            if target_piece is None or target_piece.color is not piece.color:
                moves.append(Move(position, target))

    moves.extend(_castle_moves(state, position, piece))
    return moves


def _castle_moves(state: ChessState, position: Position, piece: Piece) -> list[Move]:
    if piece.kind is not PieceType.KING:
        return []

    if piece.color is Color.WHITE and position != (7, 4):
        return []
    if piece.color is Color.BLACK and position != (0, 4):
        return []

    if _is_in_check(state, piece.color):
        return []

    moves: list[Move] = []
    rights = state.castling_rights
    row = position[0]

    if piece.color is Color.WHITE:
        if rights.white_kingside and _can_castle_kingside(state, row, Color.WHITE):
            moves.append(Move(position, (row, 6), is_castling=True))
        if rights.white_queenside and _can_castle_queenside(state, row, Color.WHITE):
            moves.append(Move(position, (row, 2), is_castling=True))
    else:
        if rights.black_kingside and _can_castle_kingside(state, row, Color.BLACK):
            moves.append(Move(position, (row, 6), is_castling=True))
        if rights.black_queenside and _can_castle_queenside(state, row, Color.BLACK):
            moves.append(Move(position, (row, 2), is_castling=True))

    return moves


def _can_castle_kingside(state: ChessState, row: int, color: Color) -> bool:
    rook_pos = (row, 7)
    if _piece_at(state, rook_pos) != Piece(color, PieceType.ROOK):
        return False
    path = [(row, 5), (row, 6)]
    if any(_piece_at(state, pos) is not None for pos in path):
        return False
    return all(
        not _is_square_attacked(state, pos, color.opponent())
        for pos in [(row, 4), *path]
    )


def _can_castle_queenside(state: ChessState, row: int, color: Color) -> bool:
    rook_pos = (row, 0)
    if _piece_at(state, rook_pos) != Piece(color, PieceType.ROOK):
        return False
    path = [(row, 3), (row, 2), (row, 1)]
    if any(_piece_at(state, pos) is not None for pos in path):
        return False
    return all(
        not _is_square_attacked(state, pos, color.opponent())
        for pos in [(row, 4), (row, 3), (row, 2)]
    )


def _apply_move(state: ChessState, move: Move) -> ChessState:
    board = [list(row) for row in state.board]
    start_row, start_col = move.start
    end_row, end_col = move.end
    piece = board[start_row][start_col]
    if piece is None:
        raise ValueError("No piece at move start")

    captured_piece = board[end_row][end_col]
    board[start_row][start_col] = None

    if move.is_en_passant:
        captured_row = start_row
        captured_piece = board[captured_row][end_col]
        board[captured_row][end_col] = None

    if move.is_castling or (
        piece.kind is PieceType.KING and abs(end_col - start_col) == 2
    ):
        rook_start_col = 7 if end_col > start_col else 0
        rook_end_col = 5 if end_col > start_col else 3
        rook_piece = board[start_row][rook_start_col]
        board[start_row][rook_start_col] = None
        board[start_row][rook_end_col] = rook_piece

    if move.promotion is not None:
        board[end_row][end_col] = Piece(piece.color, move.promotion)
    else:
        board[end_row][end_col] = piece

    next_castling = _update_castling_rights(
        state.castling_rights, piece, captured_piece, move.start, move.end
    )

    en_passant_target = None
    if piece.kind is PieceType.PAWN and abs(end_row - start_row) == 2:
        en_passant_target = ((start_row + end_row) // 2, start_col)

    halfmove_clock = state.halfmove_clock + 1
    if piece.kind is PieceType.PAWN or captured_piece is not None:
        halfmove_clock = 0

    fullmove = state.fullmove + (1 if state.active_color is Color.BLACK else 0)

    return ChessState(
        board=tuple(tuple(row) for row in board),
        active_color=state.active_color.opponent(),
        castling_rights=next_castling,
        en_passant_target=en_passant_target,
        halfmove_clock=halfmove_clock,
        fullmove=fullmove,
    )


def _update_castling_rights(
    rights: CastlingRights,
    moved_piece: Piece,
    captured_piece: Optional[Piece],
    start: Position,
    end: Position,
) -> CastlingRights:
    wk = rights.white_kingside
    wq = rights.white_queenside
    bk = rights.black_kingside
    bq = rights.black_queenside

    if moved_piece.kind is PieceType.KING:
        if moved_piece.color is Color.WHITE:
            wk = False
            wq = False
        else:
            bk = False
            bq = False

    if moved_piece.kind is PieceType.ROOK:
        if moved_piece.color is Color.WHITE:
            if start == (7, 7):
                wk = False
            if start == (7, 0):
                wq = False
        else:
            if start == (0, 7):
                bk = False
            if start == (0, 0):
                bq = False

    if captured_piece is not None and captured_piece.kind is PieceType.ROOK:
        if captured_piece.color is Color.WHITE:
            if end == (7, 7):
                wk = False
            if end == (7, 0):
                wq = False
        else:
            if end == (0, 7):
                bk = False
            if end == (0, 0):
                bq = False

    return CastlingRights(wk, wq, bk, bq)


def _is_in_check(state: ChessState, color: Color) -> bool:
    king_pos = _find_king(state.board, color)
    if king_pos is None:
        return False
    return _is_square_attacked(state, king_pos, color.opponent())


def _find_king(
    board: tuple[tuple[Optional[Piece], ...], ...], color: Color
) -> Optional[Position]:
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if (
                piece is not None
                and piece.color is color
                and piece.kind is PieceType.KING
            ):
                return row, col
    return None


def _is_square_attacked(state: ChessState, position: Position, by_color: Color) -> bool:
    row, col = position

    pawn_row = row + (1 if by_color is Color.WHITE else -1)
    for dc in (-1, 1):
        pawn_pos = (pawn_row, col + dc)
        if _is_in_bounds(pawn_pos):
            piece = _piece_at(state, pawn_pos)
            if piece == Piece(by_color, PieceType.PAWN):
                return True

    for dr, dc in _KNIGHT_OFFSETS:
        target = (row + dr, col + dc)
        if _is_in_bounds(target) and _piece_at(state, target) == Piece(
            by_color, PieceType.KNIGHT
        ):
            return True

    if _attacked_on_lines(
        state, position, by_color, _ROOK_DIRECTIONS, {PieceType.ROOK, PieceType.QUEEN}
    ):
        return True
    if _attacked_on_lines(
        state,
        position,
        by_color,
        _BISHOP_DIRECTIONS,
        {PieceType.BISHOP, PieceType.QUEEN},
    ):
        return True

    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            target = (row + dr, col + dc)
            if _is_in_bounds(target) and _piece_at(state, target) == Piece(
                by_color, PieceType.KING
            ):
                return True

    return False


def _attacked_on_lines(
    state: ChessState,
    position: Position,
    by_color: Color,
    directions: Iterable[tuple[int, int]],
    attackers: set[PieceType],
) -> bool:
    row, col = position
    for dr, dc in directions:
        step = 1
        while True:
            target = (row + dr * step, col + dc * step)
            if not _is_in_bounds(target):
                break
            piece = _piece_at(state, target)
            if piece is None:
                step += 1
                continue
            if piece.color is by_color and piece.kind in attackers:
                return True
            break
    return False


def _piece_at(state: ChessState, position: Position) -> Optional[Piece]:
    row, col = position
    return state.board[row][col]


def _is_in_bounds(position: Position) -> bool:
    row, col = position
    return 0 <= row < 8 and 0 <= col < 8
