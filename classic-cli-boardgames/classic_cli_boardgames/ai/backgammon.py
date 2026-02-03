"""Backgammon AI using a simple expectiminimax evaluation."""

from __future__ import annotations

import math
import random
from typing import Sequence

from classic_cli_boardgames.ai.search import SearchContext
from classic_cli_boardgames.core.interfaces import AIConfig, AIEngine
from classic_cli_boardgames.core.rng import create_rng
from classic_cli_boardgames.games.backgammon import (
    BackgammonEngine,
    BackgammonState,
    Color,
    Move,
    apply_move_with_dice,
)

_SCORE_JITTER = 0.4


_DICE_OUTCOMES = [((d1, d2), 1.0 / 36.0) for d1 in range(1, 7) for d2 in range(1, 7)]


class BackgammonAI(AIEngine[BackgammonState, Move]):
    """Intermediate backgammon AI with dice-aware evaluation."""

    name = "Backgammon AI"

    def __init__(self, engine: BackgammonEngine | None = None) -> None:
        self._engine = engine or BackgammonEngine()
        self._rng = random.Random()

    def choose_move(
        self,
        state: BackgammonState,
        legal_moves: Sequence[Move],
        config: AIConfig,
    ) -> Move:
        if not legal_moves:
            raise ValueError("No legal moves available")

        ai_color = state.active_color
        search_depth = max(1, min(config.difficulty.max_depth, 2))
        ctx = SearchContext(config.difficulty)
        rng = create_rng(config.seed) if config.seed is not None else self._rng

        best_score = -math.inf
        best_moves: list[Move] = []
        for move in legal_moves:
            score = self._score_move(state, move, ai_color, search_depth, ctx)
            score += rng.uniform(-_SCORE_JITTER, _SCORE_JITTER)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        return _select_tiebreaker(best_moves, rng)

    def _score_move(
        self,
        state: BackgammonState,
        move: Move,
        ai_color: Color,
        depth: int,
        ctx: SearchContext,
    ) -> float:
        ctx.nodes += 1
        next_state = apply_move_with_dice(state, move, dice=(1, 1))
        if ctx.out_of_budget():
            return self._evaluate(next_state, ai_color)

        status = self._engine.is_terminal(next_state)
        if status.is_terminal:
            return _terminal_score(status, ai_color)

        if depth <= 1:
            return self._evaluate(next_state, ai_color)

        return self._expected_opponent(next_state, ai_color, ctx)

    def _expected_opponent(
        self, state: BackgammonState, ai_color: Color, ctx: SearchContext
    ) -> float:
        total = 0.0
        for dice, probability in _DICE_OUTCOMES:
            if ctx.out_of_budget():
                break
            opponent_state = _with_dice(state, dice)
            legal_moves = self._engine.legal_moves(opponent_state)
            if not legal_moves:
                score = self._evaluate(opponent_state, ai_color)
                total += probability * score
                continue

            best_reply = math.inf
            for move in legal_moves:
                if ctx.out_of_budget():
                    break
                ctx.nodes += 1
                reply_state = apply_move_with_dice(opponent_state, move, dice=(1, 1))
                score = self._evaluate(reply_state, ai_color)
                if score < best_reply:
                    best_reply = score
            total += probability * best_reply
        return total

    def _evaluate(self, state: BackgammonState, ai_color: Color) -> float:
        opponent = ai_color.opponent()
        ai_pips = _pip_count(state, ai_color)
        opp_pips = _pip_count(state, opponent)
        pip_score = (opp_pips - ai_pips) * 0.1

        ai_off = state.off_white if ai_color is Color.WHITE else state.off_black
        opp_off = state.off_white if opponent is Color.WHITE else state.off_black
        off_score = (ai_off - opp_off) * 5.0

        ai_bar = state.bar_white if ai_color is Color.WHITE else state.bar_black
        opp_bar = state.bar_white if opponent is Color.WHITE else state.bar_black
        bar_score = (opp_bar - ai_bar) * 2.0

        return pip_score + off_score + bar_score


def _pip_count(state: BackgammonState, color: Color) -> int:
    total = 0
    if color is Color.WHITE:
        for idx, count in enumerate(state.points):
            if count > 0:
                total += (idx + 1) * count
        total += state.bar_white * 25
    else:
        for idx, count in enumerate(state.points):
            if count < 0:
                total += (24 - idx) * (-count)
        total += state.bar_black * 25
    return total


def _with_dice(state: BackgammonState, dice: tuple[int, int]) -> BackgammonState:
    return BackgammonState(
        points=state.points,
        active_color=state.active_color,
        bar_white=state.bar_white,
        bar_black=state.bar_black,
        off_white=state.off_white,
        off_black=state.off_black,
        dice=dice,
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
