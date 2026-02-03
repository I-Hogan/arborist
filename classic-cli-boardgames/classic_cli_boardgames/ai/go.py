"""Go AI implementation using depth-limited alpha-beta search."""

from __future__ import annotations

import math
import random
from typing import Sequence

from classic_cli_boardgames.ai.search import SearchContext
from classic_cli_boardgames.core.interfaces import AIConfig, AIEngine
from classic_cli_boardgames.core.rng import create_rng
from classic_cli_boardgames.games.go import (
    BOARD_SIZE,
    Color,
    GoEngine,
    GoState,
    Move,
    compute_area_score,
    iter_groups,
)

_CANDIDATE_LIMIT = 12
_SCORE_JITTER = 0.2


class GoAI(AIEngine[GoState, Move]):
    """Intermediate Go AI with heuristic evaluation."""

    name = "Go AI"

    def __init__(self, engine: GoEngine | None = None) -> None:
        self._engine = engine or GoEngine()
        self._rng = random.Random()

    def choose_move(
        self,
        state: GoState,
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
        for move in self._ranked_moves(state, legal_moves)[
            : _candidate_limit(legal_moves)
        ]:
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
        state: GoState,
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
        ranked_moves = self._ranked_moves(state, moves)[: _candidate_limit(moves)]

        if maximizing:
            value = -math.inf
            for move in ranked_moves:
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
        for move in ranked_moves:
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

    def _ranked_moves(self, state: GoState, moves: Sequence[Move]) -> list[Move]:
        scored: list[tuple[float, Move]] = []
        for move in moves:
            scored.append((self._quick_score(state, move), move))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [move for _, move in scored]

    def _quick_score(self, state: GoState, move: Move) -> float:
        if move.is_pass:
            return -0.5
        if move.position is None:
            return -0.5
        row, col = move.position
        center_distance = _center_distance(row, col)
        score = -0.05 * center_distance

        opponent = state.active_color.opponent()
        adjacent_opponent = 0
        adjacent_friend = 0
        for neighbor in _neighbors(row, col):
            stone = state.board[neighbor[0]][neighbor[1]]
            if stone is None:
                continue
            if stone.color is opponent:
                adjacent_opponent += 1
            else:
                adjacent_friend += 1
        score += 0.35 * adjacent_opponent + 0.15 * adjacent_friend

        next_state = self._engine.apply_move(state, move)
        if state.active_color is Color.BLACK:
            capture_gain = next_state.captures_black - state.captures_black
        else:
            capture_gain = next_state.captures_white - state.captures_white
        score += 1.5 * capture_gain
        return score

    def _evaluate(self, state: GoState, ai_color: Color) -> float:
        black_area, white_area = compute_area_score(state.board)
        area_diff = black_area - white_area
        if ai_color is Color.WHITE:
            area_diff = -area_diff

        capture_diff = state.captures_black - state.captures_white
        if ai_color is Color.WHITE:
            capture_diff = -capture_diff

        liberties_ai, liberties_opp, atari_ai, atari_opp = _liberty_stats(
            state, ai_color
        )
        score = float(area_diff)
        score += 0.2 * capture_diff
        score += 0.04 * (liberties_ai - liberties_opp)
        score += 0.4 * atari_opp
        score -= 0.4 * atari_ai
        return score


def _terminal_score(status, ai_color: Color) -> float:
    if status.outcome is None or status.outcome.winner is None:
        return 0.0
    if status.outcome.winner == ai_color.label:
        return 10000.0
    return -10000.0


def _candidate_limit(moves: Sequence[Move]) -> int:
    if len(moves) <= _CANDIDATE_LIMIT:
        return len(moves)
    return _CANDIDATE_LIMIT


def _center_distance(row: int, col: int) -> float:
    center = (BOARD_SIZE - 1) / 2.0
    return abs(row - center) + abs(col - center)


def _neighbors(row: int, col: int) -> list[tuple[int, int]]:
    neighbors: list[tuple[int, int]] = []
    if row > 0:
        neighbors.append((row - 1, col))
    if row < BOARD_SIZE - 1:
        neighbors.append((row + 1, col))
    if col > 0:
        neighbors.append((row, col - 1))
    if col < BOARD_SIZE - 1:
        neighbors.append((row, col + 1))
    return neighbors


def _liberty_stats(state: GoState, ai_color: Color) -> tuple[int, int, int, int]:
    liberties_ai = 0
    liberties_opp = 0
    atari_ai = 0
    atari_opp = 0
    for color, _, liberties in iter_groups(state.board):
        if color is ai_color:
            liberties_ai += len(liberties)
            if len(liberties) == 1:
                atari_ai += 1
        else:
            liberties_opp += len(liberties)
            if len(liberties) == 1:
                atari_opp += 1
    return liberties_ai, liberties_opp, atari_ai, atari_opp


def _select_tiebreaker(
    moves: Sequence[Move],
    rng: random.Random,
) -> Move:
    if len(moves) == 1:
        return moves[0]
    return rng.choice(list(moves))
