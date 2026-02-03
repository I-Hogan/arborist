"""Session management for the local web UI."""

from __future__ import annotations

from dataclasses import dataclass, field
import threading
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar
import uuid

from classic_cli_boardgames.ai.backgammon import BackgammonAI
from classic_cli_boardgames.ai.chess import ChessAI
from classic_cli_boardgames.ai.checkers import CheckersAI
from classic_cli_boardgames.ai.difficulty import DEFAULT_DIFFICULTY, DIFFICULTY_OPTIONS
from classic_cli_boardgames.ai.go import GoAI
from classic_cli_boardgames.cli.ai_setup import (
    DEFAULT_PLAYER_MODE,
    PLAYER_MODE_OPTIONS,
    PlayerModeOption,
)
from classic_cli_boardgames.cli.help_text import (
    BACKGAMMON_HELP,
    CHECKERS_HELP,
    CHESS_HELP,
    GO_HELP,
)
from classic_cli_boardgames.core.interfaces import AIConfig, AIEngine, GameEngine
from classic_cli_boardgames.games.backgammon import (
    BackgammonEngine,
    Color as BackgammonColor,
    parse_move_input as parse_backgammon_move,
)
from classic_cli_boardgames.games.checkers import (
    CheckersEngine,
    Color as CheckersColor,
    parse_move_input as parse_checkers_move,
)
from classic_cli_boardgames.games.chess import (
    ChessEngine,
    Color as ChessColor,
    parse_move_input as parse_chess_move,
)
from classic_cli_boardgames.games.go import (
    Color as GoColor,
    GoEngine,
    parse_move_input as parse_go_move,
)

StateT = TypeVar("StateT")
MoveT = TypeVar("MoveT")


@dataclass(frozen=True)
class GameDefinition(Generic[StateT, MoveT]):
    key: str
    name: str
    engine_factory: Callable[[Optional[int]], GameEngine[StateT, MoveT]]
    ai_factory: Callable[[GameEngine[StateT, MoveT]], AIEngine[StateT, MoveT]]
    parse_move: Callable[[str, Sequence[MoveT]], tuple[Optional[MoveT], Optional[str]]]
    help_text: str
    human_color: Any


GAME_DEFINITIONS: dict[str, GameDefinition[Any, Any]] = {
    "chess": GameDefinition(
        key="chess",
        name="Chess",
        engine_factory=lambda seed: ChessEngine(),
        ai_factory=lambda engine: ChessAI(engine),
        parse_move=parse_chess_move,
        help_text=CHESS_HELP,
        human_color=ChessColor.WHITE,
    ),
    "checkers": GameDefinition(
        key="checkers",
        name="Checkers",
        engine_factory=lambda seed: CheckersEngine(),
        ai_factory=lambda engine: CheckersAI(engine),
        parse_move=parse_checkers_move,
        help_text=CHECKERS_HELP,
        human_color=CheckersColor.WHITE,
    ),
    "backgammon": GameDefinition(
        key="backgammon",
        name="Backgammon",
        engine_factory=lambda seed: BackgammonEngine(seed=seed),
        ai_factory=lambda engine: BackgammonAI(engine),
        parse_move=parse_backgammon_move,
        help_text=BACKGAMMON_HELP,
        human_color=BackgammonColor.WHITE,
    ),
    "go": GameDefinition(
        key="go",
        name="Go",
        engine_factory=lambda seed: GoEngine(),
        ai_factory=lambda engine: GoAI(engine),
        parse_move=parse_go_move,
        help_text=GO_HELP,
        human_color=GoColor.BLACK,
    ),
}

MAX_LOG_ENTRIES = 200


@dataclass
class GameSession(Generic[StateT, MoveT]):
    session_id: str
    definition: GameDefinition[StateT, MoveT]
    engine: GameEngine[StateT, MoveT]
    ai: AIEngine[StateT, MoveT]
    config: AIConfig
    player_mode: PlayerModeOption
    state: StateT
    human_color: Any
    ai_color: Any
    log: list[str] = field(default_factory=list)

    def reset(self) -> None:
        self.state = self.engine.new_game()
        self.log.clear()


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, GameSession[Any, Any]] = {}
        self._lock = threading.Lock()

    def create_session(
        self,
        game_key: str,
        difficulty_key: Optional[str] = None,
        mode_key: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> dict[str, Any]:
        definition = GAME_DEFINITIONS.get(game_key)
        if definition is None:
            raise ValueError("Unknown game")

        difficulty = _difficulty_from_key(difficulty_key)
        mode = _mode_from_key(mode_key)

        engine = definition.engine_factory(seed)
        ai = definition.ai_factory(engine)
        config = AIConfig(difficulty=difficulty, seed=seed)
        state = engine.new_game()
        human_color = definition.human_color
        ai_color = human_color.opponent()
        session = GameSession(
            session_id=uuid.uuid4().hex,
            definition=definition,
            engine=engine,
            ai=ai,
            config=config,
            player_mode=mode,
            state=state,
            human_color=human_color,
            ai_color=ai_color,
        )
        _append_log(session, f"New {definition.name} game started: {mode.name}.")
        _maybe_auto_ai(session)
        with self._lock:
            self._sessions[session.session_id] = session
        return _serialize_session(session)

    def get_session(self, session_id: str) -> Optional[GameSession[Any, Any]]:
        with self._lock:
            return self._sessions.get(session_id)

    def delete_session(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def list_options(self) -> dict[str, Any]:
        return build_options_payload()

    def snapshot(self, session_id: str) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found")
        return _serialize_session(session)

    def handle_action(self, session_id: str, action: dict[str, Any]) -> dict[str, Any]:
        session = self.get_session(session_id)
        if session is None:
            raise KeyError("Session not found")

        action_type = (action.get("type") or "").strip().lower()
        if action_type == "move":
            text = str(action.get("text", ""))
            message = _handle_move(session, text)
            return {
                "ok": True,
                "message": message,
                "session": _serialize_session(session),
            }
        if action_type == "restart":
            session.reset()
            _append_log(session, "Game restarted.")
            _maybe_auto_ai(session)
            return {"ok": True, "session": _serialize_session(session)}
        if action_type == "ai_step":
            message = _advance_ai(session)
            return {
                "ok": True,
                "message": message,
                "session": _serialize_session(session),
            }
        if action_type == "help":
            return {"ok": True, "help": session.definition.help_text}
        if action_type == "end":
            self.delete_session(session_id)
            return {"ok": True, "ended": True}

        return {"ok": False, "error": "Unknown action."}


SESSION_STORE = SessionStore()


def build_options_payload() -> dict[str, Any]:
    games = [
        {"key": definition.key, "name": definition.name}
        for definition in GAME_DEFINITIONS.values()
    ]
    difficulties = [
        {
            "key": option.key,
            "name": option.name,
            "description": option.description,
        }
        for option in DIFFICULTY_OPTIONS
    ]
    player_modes = [
        {
            "key": option.key,
            "name": option.name,
            "description": option.description,
            "ai_vs_ai": option.ai_vs_ai,
        }
        for option in PLAYER_MODE_OPTIONS
    ]

    return {
        "games": games,
        "difficulties": difficulties,
        "player_modes": player_modes,
        "defaults": {
            "game": "chess",
            "difficulty": _difficulty_key(DEFAULT_DIFFICULTY),
            "player_mode": _mode_key(DEFAULT_PLAYER_MODE),
        },
        "help": {
            key: definition.help_text for key, definition in GAME_DEFINITIONS.items()
        },
    }


def _difficulty_key(difficulty) -> str:
    for option in DIFFICULTY_OPTIONS:
        if option.difficulty == difficulty:
            return option.key
    return DIFFICULTY_OPTIONS[0].key


def _difficulty_from_key(key: Optional[str]) -> Any:
    if key:
        for option in DIFFICULTY_OPTIONS:
            if option.key == key:
                return option.difficulty
    return DEFAULT_DIFFICULTY


def _mode_key(mode: PlayerModeOption) -> str:
    for option in PLAYER_MODE_OPTIONS:
        if option is mode:
            return option.key
    return PLAYER_MODE_OPTIONS[0].key


def _mode_from_key(key: Optional[str]) -> PlayerModeOption:
    if key:
        for option in PLAYER_MODE_OPTIONS:
            if option.key == key:
                return option
    return DEFAULT_PLAYER_MODE


def _serialize_session(session: GameSession[Any, Any]) -> dict[str, Any]:
    status = session.engine.is_terminal(session.state)
    has_moves = bool(session.engine.legal_moves(session.state))
    outcome = None
    if status.outcome is not None:
        outcome = {
            "winner": status.outcome.winner,
            "reason": status.outcome.reason,
        }
    return {
        "id": session.session_id,
        "game": session.definition.name,
        "game_key": session.definition.key,
        "difficulty": session.config.difficulty.name,
        "player_mode": session.player_mode.name,
        "ai_vs_ai": session.player_mode.ai_vs_ai,
        "active_color": session.state.active_color.label,
        "render": session.engine.render(session.state),
        "terminal": status.is_terminal,
        "outcome": outcome,
        "has_moves": has_moves,
        "human_can_move": _human_can_move(session, status.is_terminal),
        "log": list(session.log[-MAX_LOG_ENTRIES:]),
    }


def _human_can_move(session: GameSession[Any, Any], is_terminal: bool) -> bool:
    if is_terminal:
        return False
    if session.player_mode.ai_vs_ai:
        return False
    return session.state.active_color is session.human_color


def _append_log(session: GameSession[Any, Any], message: str) -> None:
    session.log.append(message)
    if len(session.log) > MAX_LOG_ENTRIES:
        session.log[:] = session.log[-MAX_LOG_ENTRIES:]


def _handle_move(session: GameSession[Any, Any], text: str) -> str:
    status = session.engine.is_terminal(session.state)
    if status.is_terminal:
        return "The game is over. Restart to play again."

    if session.player_mode.ai_vs_ai:
        return "Auto-play is enabled. Use Next Move for AI turns."

    if session.state.active_color is not session.human_color:
        return "It is not your turn yet."

    legal_moves = session.engine.legal_moves(session.state)
    if not legal_moves and _supports_pass_turn(session.engine):
        session.state = session.engine.pass_turn(session.state)
        message = "No legal moves. Passing turn."
        _append_log(session, message)
        _maybe_auto_ai(session)
        return message

    move, error = session.definition.parse_move(text, legal_moves)
    if move is None:
        return error or "Invalid move."

    session.state = session.engine.apply_move(session.state, move)
    message = f"You ({session.human_color.label}) played {_format_move(move)}."
    _append_log(session, message)
    _maybe_auto_ai(session)
    return message


def _maybe_auto_ai(session: GameSession[Any, Any]) -> None:
    if session.player_mode.ai_vs_ai:
        return
    if session.state.active_color is session.ai_color:
        _advance_ai(session)


def _advance_ai(session: GameSession[Any, Any]) -> str:
    status = session.engine.is_terminal(session.state)
    if status.is_terminal:
        return "The game is already finished."

    legal_moves = session.engine.legal_moves(session.state)
    if not legal_moves and _supports_pass_turn(session.engine):
        session.state = session.engine.pass_turn(session.state)
        message = (
            f"Computer ({session.state.active_color.opponent().label}) has no legal moves. "
            "Passing turn."
        )
        _append_log(session, message)
        return message

    if not legal_moves:
        return "No legal moves available."

    move = session.ai.choose_move(session.state, legal_moves, session.config)
    message = (
        f"Computer ({session.state.active_color.label}) plays {_format_move(move)}."
    )
    session.state = session.engine.apply_move(session.state, move)
    _append_log(session, message)
    return message


def _format_move(move: Any) -> str:
    notation = getattr(move, "notation", None)
    if callable(notation):
        return notation()
    return str(move)


def _supports_pass_turn(engine: GameEngine[Any, Any]) -> bool:
    return hasattr(engine, "pass_turn")
