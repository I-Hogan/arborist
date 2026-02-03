from classic_cli_boardgames.games.backgammon import (
    BAR,
    OFF,
    BackgammonEngine,
    BackgammonState,
    Color as BackgammonColor,
)
from classic_cli_boardgames.games.checkers import (
    CheckersEngine,
    CheckersState,
    Color as CheckersColor,
    Move as CheckersMove,
    Piece as CheckersPiece,
    PieceType as CheckersPieceType,
)
from classic_cli_boardgames.games.chess import (
    CastlingRights,
    ChessEngine,
    ChessState,
    Color as ChessColor,
    Piece as ChessPiece,
    PieceType as ChessPieceType,
    algebraic_to_position,
)
from classic_cli_boardgames.games.go import (
    BOARD_SIZE,
    Color as GoColor,
    GoEngine,
    GoState,
    Move as GoMove,
    Stone as GoStone,
)


def _empty_board() -> tuple[tuple[None, ...], ...]:
    return tuple(tuple(None for _ in range(8)) for _ in range(8))


def _place_chess(
    pieces: dict[tuple[int, int], ChessPiece],
) -> tuple[tuple[ChessPiece | None, ...], ...]:
    board = [list(row) for row in _empty_board()]
    for (row, col), piece in pieces.items():
        board[row][col] = piece
    return tuple(tuple(row) for row in board)


def _place_checkers(
    pieces: dict[tuple[int, int], CheckersPiece],
) -> tuple[tuple[CheckersPiece | None, ...], ...]:
    board = [list(row) for row in _empty_board()]
    for (row, col), piece in pieces.items():
        board[row][col] = piece
    return tuple(tuple(row) for row in board)


def _empty_go_board() -> tuple[tuple[GoStone | None, ...], ...]:
    return tuple(tuple(None for _ in range(BOARD_SIZE)) for _ in range(BOARD_SIZE))


def _place_go(
    stones: dict[tuple[int, int], GoStone],
) -> tuple[tuple[GoStone | None, ...], ...]:
    board = [list(row) for row in _empty_go_board()]
    for (row, col), stone in stones.items():
        board[row][col] = stone
    return tuple(tuple(row) for row in board)


def test_chess_initial_legal_moves() -> None:
    engine = ChessEngine()
    state = engine.new_game()
    moves = engine.legal_moves(state)
    assert len(moves) == 20
    notations = {move.notation() for move in moves}
    assert "e2e4" in notations
    assert "g1f3" in notations


def test_chess_castling_available_on_clear_board() -> None:
    engine = ChessEngine()
    pieces = {
        (7, 4): ChessPiece(ChessColor.WHITE, ChessPieceType.KING),
        (7, 0): ChessPiece(ChessColor.WHITE, ChessPieceType.ROOK),
        (7, 7): ChessPiece(ChessColor.WHITE, ChessPieceType.ROOK),
        (0, 4): ChessPiece(ChessColor.BLACK, ChessPieceType.KING),
    }
    state = ChessState(
        board=_place_chess(pieces),
        active_color=ChessColor.WHITE,
        castling_rights=CastlingRights(True, True, False, False),
        en_passant_target=None,
        halfmove_clock=0,
        fullmove=1,
    )
    moves = engine.legal_moves(state)
    castle_ends = {move.end for move in moves if move.is_castling}
    assert castle_ends == {(7, 6), (7, 2)}


def test_chess_en_passant_move_generated() -> None:
    engine = ChessEngine()
    white_pawn = ChessPiece(ChessColor.WHITE, ChessPieceType.PAWN)
    black_pawn = ChessPiece(ChessColor.BLACK, ChessPieceType.PAWN)
    pieces = {
        algebraic_to_position("e5"): white_pawn,
        algebraic_to_position("d5"): black_pawn,
        (7, 4): ChessPiece(ChessColor.WHITE, ChessPieceType.KING),
        (0, 4): ChessPiece(ChessColor.BLACK, ChessPieceType.KING),
    }
    en_passant_target = algebraic_to_position("d6")
    state = ChessState(
        board=_place_chess(pieces),
        active_color=ChessColor.WHITE,
        castling_rights=CastlingRights(False, False, False, False),
        en_passant_target=en_passant_target,
        halfmove_clock=0,
        fullmove=1,
    )
    moves = engine.legal_moves(state)
    assert any(
        move.is_en_passant
        and move.start == algebraic_to_position("e5")
        and move.end == en_passant_target
        for move in moves
    )


def test_checkers_capture_required() -> None:
    engine = CheckersEngine()
    pieces = {
        (2, 1): CheckersPiece(CheckersColor.BLACK, CheckersPieceType.MAN),
        (3, 2): CheckersPiece(CheckersColor.WHITE, CheckersPieceType.MAN),
    }
    state = CheckersState(
        board=_place_checkers(pieces), active_color=CheckersColor.BLACK
    )
    moves = engine.legal_moves(state)
    assert moves
    assert all(move.is_capture for move in moves)
    assert moves[0].path == ((2, 1), (4, 3))


def test_checkers_multi_jump_capture_sequence() -> None:
    engine = CheckersEngine()
    pieces = {
        (2, 1): CheckersPiece(CheckersColor.BLACK, CheckersPieceType.MAN),
        (3, 2): CheckersPiece(CheckersColor.WHITE, CheckersPieceType.MAN),
        (5, 4): CheckersPiece(CheckersColor.WHITE, CheckersPieceType.MAN),
    }
    state = CheckersState(
        board=_place_checkers(pieces), active_color=CheckersColor.BLACK
    )
    moves = engine.legal_moves(state)
    assert any(
        move.path == ((2, 1), (4, 3), (6, 5)) and move.captures == ((3, 2), (5, 4))
        for move in moves
    )


def test_checkers_promotion_to_king() -> None:
    engine = CheckersEngine()
    pieces = {
        (6, 1): CheckersPiece(CheckersColor.BLACK, CheckersPieceType.MAN),
    }
    state = CheckersState(
        board=_place_checkers(pieces), active_color=CheckersColor.BLACK
    )
    move = CheckersMove(path=((6, 1), (7, 0)))
    next_state = engine.apply_move(state, move)
    promoted = next_state.board[7][0]
    assert promoted is not None
    assert promoted.kind == CheckersPieceType.KING


def test_backgammon_bar_entry_blocked() -> None:
    engine = BackgammonEngine(seed=1)
    points = [0] * 24
    points[21] = -2
    points[20] = -2
    state = BackgammonState(
        points=tuple(points),
        active_color=BackgammonColor.WHITE,
        bar_white=1,
        bar_black=0,
        off_white=0,
        off_black=0,
        dice=(3, 4),
    )
    moves = engine.legal_moves(state)
    assert moves == []


def test_backgammon_bar_entry_available() -> None:
    engine = BackgammonEngine(seed=1)
    points = [0] * 24
    points[20] = -2
    points[17] = -2
    state = BackgammonState(
        points=tuple(points),
        active_color=BackgammonColor.WHITE,
        bar_white=1,
        bar_black=0,
        off_white=0,
        off_black=0,
        dice=(3, 4),
    )
    moves = engine.legal_moves(state)
    assert len(moves) == 1
    step = moves[0].steps[0]
    assert step.start == BAR
    assert step.die == 3


def test_backgammon_bear_off_uses_high_die_when_one_checker() -> None:
    engine = BackgammonEngine(seed=1)
    points = [0] * 24
    points[0] = 1
    state = BackgammonState(
        points=tuple(points),
        active_color=BackgammonColor.WHITE,
        bar_white=0,
        bar_black=0,
        off_white=0,
        off_black=0,
        dice=(1, 6),
    )
    moves = engine.legal_moves(state)
    assert len(moves) == 1
    step = moves[0].steps[0]
    assert step.end == OFF
    assert step.die == 6


def test_go_capture_and_score_tracking() -> None:
    engine = GoEngine()
    stones = {
        (4, 4): GoStone(GoColor.WHITE),
        (4, 3): GoStone(GoColor.BLACK),
        (4, 5): GoStone(GoColor.BLACK),
        (3, 4): GoStone(GoColor.BLACK),
    }
    state = GoState(
        board=_place_go(stones),
        active_color=GoColor.BLACK,
        previous_board=None,
        consecutive_passes=0,
        captures_black=0,
        captures_white=0,
    )
    next_state = engine.apply_move(state, GoMove((5, 4)))
    assert next_state.board[4][4] is None
    assert next_state.captures_black == 1


def test_go_suicide_is_illegal() -> None:
    engine = GoEngine()
    stones = {
        (4, 3): GoStone(GoColor.WHITE),
        (4, 5): GoStone(GoColor.WHITE),
        (3, 4): GoStone(GoColor.WHITE),
        (5, 4): GoStone(GoColor.WHITE),
    }
    state = GoState(
        board=_place_go(stones),
        active_color=GoColor.BLACK,
        previous_board=None,
        consecutive_passes=0,
        captures_black=0,
        captures_white=0,
    )
    moves = engine.legal_moves(state)
    assert all(move.position != (4, 4) for move in moves)


def test_go_two_passes_end_game() -> None:
    engine = GoEngine()
    state = engine.new_game()
    state = engine.apply_move(state, GoMove())
    state = engine.apply_move(state, GoMove())
    status = engine.is_terminal(state)
    assert status.is_terminal is True
