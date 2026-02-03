from classic_cli_boardgames.ai.backgammon import BackgammonAI
from classic_cli_boardgames.ai.checkers import CheckersAI
from classic_cli_boardgames.ai.chess import ChessAI
from classic_cli_boardgames.ai.go import GoAI
from classic_cli_boardgames.core.interfaces import AIDifficulty, AIConfig
from classic_cli_boardgames.games.backgammon import (
    BackgammonEngine,
    BackgammonState,
    Color as BackgammonColor,
)
from classic_cli_boardgames.games.checkers import CheckersEngine
from classic_cli_boardgames.games.chess import ChessEngine
from classic_cli_boardgames.games.go import GoEngine

TEST_DIFFICULTY = AIDifficulty("Test", max_depth=1, max_nodes=200)


def _config(seed: int) -> AIConfig:
    return AIConfig(difficulty=TEST_DIFFICULTY, seed=seed)


def test_chess_ai_seeded_determinism() -> None:
    engine = ChessEngine()
    state = engine.new_game()
    moves = engine.legal_moves(state)
    ai = ChessAI(engine)
    config = _config(123)
    first = ai.choose_move(state, moves, config)
    second = ai.choose_move(state, moves, config)
    assert first == second


def test_checkers_ai_seeded_determinism() -> None:
    engine = CheckersEngine()
    state = engine.new_game()
    moves = engine.legal_moves(state)
    ai = CheckersAI(engine)
    config = _config(456)
    first = ai.choose_move(state, moves, config)
    second = ai.choose_move(state, moves, config)
    assert first == second


def test_backgammon_ai_seeded_determinism() -> None:
    engine = BackgammonEngine(seed=99)
    base_state = engine.new_game()
    state = BackgammonState(
        points=base_state.points,
        active_color=BackgammonColor.WHITE,
        bar_white=base_state.bar_white,
        bar_black=base_state.bar_black,
        off_white=base_state.off_white,
        off_black=base_state.off_black,
        dice=(3, 4),
    )
    moves = engine.legal_moves(state)
    ai = BackgammonAI(engine)
    config = _config(789)
    first = ai.choose_move(state, moves, config)
    second = ai.choose_move(state, moves, config)
    assert first == second


def test_go_ai_seeded_determinism() -> None:
    engine = GoEngine()
    state = engine.new_game()
    moves = engine.legal_moves(state)
    ai = GoAI(engine)
    config = _config(202)
    first = ai.choose_move(state, moves, config)
    second = ai.choose_move(state, moves, config)
    assert first == second
