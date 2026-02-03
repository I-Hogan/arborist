"""Chess AI implementation using depth-limited alpha-beta search."""

from __future__ import annotations

import math
import random
from typing import Sequence

from classic_cli_boardgames.ai.search import SearchContext
from classic_cli_boardgames.core.interfaces import AIConfig, AIEngine
from classic_cli_boardgames.core.rng import create_rng
from classic_cli_boardgames.games.chess import (
    ChessEngine,
    ChessState,
    Color,
    Move,
    PieceType,
)


_PIECE_VALUES = {
    PieceType.PAWN: 1.0,
    PieceType.KNIGHT: 3.0,
    PieceType.BISHOP: 3.25,
    PieceType.ROOK: 5.0,
    PieceType.QUEEN: 9.0,
    PieceType.KING: 0.0,
}

_CENTER_SQUARES = {(3, 3), (3, 4), (4, 3), (4, 4)}
_SCORE_JITTER = 0.05


class ChessAI(AIEngine[ChessState, Move]):
    """Intermediate chess AI with alpha-beta pruning."""

    name = "Chess AI"

    def __init__(self, engine: ChessEngine | None = None) -> None:
        self._engine = engine or ChessEngine()
        self._rng = random.Random()

    def choose_move(
        self,
        state: ChessState,
        legal_moves: Sequence[Move],
        config: AIConfig,
    ) -> Move:
        if not legal_moves:
            raise ValueError("No legal moves available")

        ai_color = state.active_color
        depth = max(config.difficulty.max_depth - 1, 0)
        ctx = SearchContext(config.difficulty)
        rng = create_rng(config.seed) if config.seed is not None else self._rng

        best_score = -math.inf
        best_moves: list[Move] = []
        for move in legal_moves:
            next_state = self._engine.apply_move(state, move)
            score = self._alpha_beta(
                next_state, depth, -math.inf, math.inf, ai_color, ctx
            )
            score += rng.uniform(-_SCORE_JITTER, _SCORE_JITTER)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        return _select_tiebreaker(best_moves, rng)

    def _alpha_beta(
        self,
        state: ChessState,
        depth: int,
        alpha: float,
        beta: float,
        ai_color: Color,
        ctx: SearchContext,
    ) -> float:
        ctx.nodes += 1
        if ctx.out_of_budget():
            return self._evaluate(state, ai_color)

        status = self._engine.is_terminal(state)
        if status.is_terminal:
            return _terminal_score(status, ai_color)

        if depth <= 0:
            return self._evaluate(state, ai_color)

        moves = self._engine.legal_moves(state)
        if not moves:
            return self._evaluate(state, ai_color)

        maximizing = state.active_color is ai_color
        if maximizing:
            value = -math.inf
            for move in moves:
                value = max(
                    value,
                    self._alpha_beta(
                        self._engine.apply_move(state, move),
                        depth - 1,
                        alpha,
                        beta,
                        ai_color,
                        ctx,
                    ),
                )
                alpha = max(alpha, value)
                if alpha >= beta or ctx.out_of_budget():
                    break
            return value

        value = math.inf
        for move in moves:
            value = min(
                value,
                self._alpha_beta(
                    self._engine.apply_move(state, move),
                    depth - 1,
                    alpha,
                    beta,
                    ai_color,
                    ctx,
                ),
            )
            beta = min(beta, value)
            if alpha >= beta or ctx.out_of_budget():
                break
        return value

    def _evaluate(self, state: ChessState, ai_color: Color) -> float:
        score = 0.0
        for row_index, row in enumerate(state.board):
            for col_index, piece in enumerate(row):
                if piece is None:
                    continue
                value = _PIECE_VALUES[piece.kind]
                bonus = 0.0
                if piece.kind is PieceType.PAWN:
                    if piece.color is Color.WHITE:
                        bonus += max(0, 6 - row_index) * 0.05
                    else:
                        bonus += max(0, row_index - 1) * 0.05
                if (
                    piece.kind is not PieceType.KING
                    and (row_index, col_index) in _CENTER_SQUARES
                ):
                    bonus += 0.1

                if piece.color is ai_color:
                    score += value + bonus
                else:
                    score -= value + bonus

        score += 0.05 * self._mobility_score(state, ai_color)
        return score

    def _mobility_score(self, state: ChessState, ai_color: Color) -> float:
        ai_state = _with_active_color(state, ai_color)
        opp_state = _with_active_color(state, ai_color.opponent())
        ai_moves = len(self._engine.legal_moves(ai_state))
        opp_moves = len(self._engine.legal_moves(opp_state))
        return float(ai_moves - opp_moves)


def _with_active_color(state: ChessState, color: Color) -> ChessState:
    return ChessState(
        board=state.board,
        active_color=color,
        castling_rights=state.castling_rights,
        en_passant_target=state.en_passant_target,
        halfmove_clock=state.halfmove_clock,
        fullmove=state.fullmove,
    )


def _terminal_score(status, ai_color: Color) -> float:
    if status.outcome is None or status.outcome.winner is None:
        return 0.0
    if status.outcome.winner == ai_color.label:
        return 10000.0
    return -10000.0


def _select_tiebreaker(
    moves: Sequence[Move],
    rng: random.Random,
) -> Move:
    if len(moves) == 1:
        return moves[0]
    return rng.choice(list(moves))
