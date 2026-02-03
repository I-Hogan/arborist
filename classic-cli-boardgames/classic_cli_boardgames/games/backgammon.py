"""Backgammon rules, move generation, and rendering."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence

from classic_cli_boardgames.core.interfaces import GameOutcome, TerminalStatus
from classic_cli_boardgames.core.parsing import split_tokens
from classic_cli_boardgames.core.rendering import render_grid
from classic_cli_boardgames.core.rng import create_rng

TOTAL_CHECKERS = 15
POINTS_COUNT = 24
BAR = -1
OFF = 24


class Color(str, Enum):
    WHITE = "white"
    BLACK = "black"

    def opponent(self) -> "Color":
        return Color.BLACK if self is Color.WHITE else Color.WHITE

    @property
    def label(self) -> str:
        return "White" if self is Color.WHITE else "Black"


@dataclass(frozen=True)
class Step:
    start: int
    end: int
    die: int
    hit: bool = False

    def notation(self) -> str:
        return f"{_format_location(self.start, start=True)}/{_format_location(self.end, start=False)}"


@dataclass(frozen=True)
class Move:
    steps: tuple[Step, ...]

    def notation(self) -> str:
        if not self.steps:
            return "pass"
        return " ".join(step.notation() for step in self.steps)


@dataclass(frozen=True)
class BackgammonState:
    points: tuple[int, ...]
    active_color: Color
    bar_white: int
    bar_black: int
    off_white: int
    off_black: int
    dice: tuple[int, int]


class BackgammonEngine:
    """Backgammon rules engine."""

    name = "Backgammon"

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = create_rng(seed)

    def new_game(self) -> BackgammonState:
        return BackgammonState(
            points=_initial_board(),
            active_color=Color.WHITE,
            bar_white=0,
            bar_black=0,
            off_white=0,
            off_black=0,
            dice=_roll_dice(self._rng),
        )

    def legal_moves(self, state: BackgammonState) -> Sequence[Move]:
        return _legal_moves(state)

    def apply_move(self, state: BackgammonState, move: Move) -> BackgammonState:
        return _apply_move(state, move, self._rng)

    def pass_turn(self, state: BackgammonState) -> BackgammonState:
        return _advance_turn(state, self._rng)

    def is_terminal(self, state: BackgammonState) -> TerminalStatus:
        if state.off_white >= TOTAL_CHECKERS:
            return TerminalStatus(True, GameOutcome("White", "borne off all checkers"))
        if state.off_black >= TOTAL_CHECKERS:
            return TerminalStatus(True, GameOutcome("Black", "borne off all checkers"))
        return TerminalStatus(False, None)

    def render(self, state: BackgammonState) -> str:
        return render_state(state)


def parse_move_input(
    text: str, legal_moves: Sequence[Move]
) -> tuple[Optional[Move], Optional[str]]:
    tokens = split_tokens(text.replace(",", " "))
    if not tokens:
        return None, "Enter moves like 24/23 13/11 or bar/24 6/off."

    pairs: list[tuple[int, int]] = []
    for token in tokens:
        cleaned = token.strip()
        if not cleaned:
            continue
        parts = _split_move_token(cleaned)
        if parts is None:
            return None, "Moves must be start/end pairs separated by '-' or '/'."
        start_text, end_text = parts
        start = _parse_location(start_text, start=True)
        if start is None:
            return None, "Start must be a point number (1-24) or 'bar'."
        end = _parse_location(end_text, start=False)
        if end is None:
            return None, "End must be a point number (1-24) or 'off'."
        pairs.append((start, end))

    if not pairs:
        return None, "Enter at least one move."

    for move in legal_moves:
        if len(move.steps) != len(pairs):
            continue
        if all(
            step.start == start and step.end == end
            for step, (start, end) in zip(move.steps, pairs)
        ):
            return move, None

    return None, "That move sequence is not legal."


def render_state(state: BackgammonState) -> str:
    lines = [
        f"Turn: {state.active_color.label}",
        _dice_line(state.dice),
        f"Bar: White {state.bar_white} | Black {state.bar_black}",
        f"Off: White {state.off_white} | Black {state.off_black}",
        "",
        _render_board(state.points),
    ]
    if _bar_count(state, state.active_color) > 0:
        lines.append(f"{state.active_color.label} must enter from the bar.")
    return "\n".join(lines)


def _split_move_token(token: str) -> Optional[tuple[str, str]]:
    for separator in ("->", "-", "/"):
        if separator in token:
            parts = [part.strip() for part in token.split(separator) if part.strip()]
            if len(parts) == 2:
                return parts[0], parts[1]
            return None
    return None


def _parse_location(token: str, *, start: bool) -> Optional[int]:
    cleaned = token.strip().lower()
    if start and cleaned == "bar":
        return BAR
    if not start and cleaned == "off":
        return OFF
    if cleaned.isdigit():
        value = int(cleaned, 10)
        if 1 <= value <= POINTS_COUNT:
            return value - 1
    return None


def _format_location(location: int, *, start: bool) -> str:
    if location == BAR and start:
        return "bar"
    if location == OFF and not start:
        return "off"
    if 0 <= location < POINTS_COUNT:
        return str(location + 1)
    return "?"


def _dice_line(dice: tuple[int, int]) -> str:
    if dice[0] == dice[1]:
        return f"Dice: {dice[0]}, {dice[1]} (doubles)"
    return f"Dice: {dice[0]}, {dice[1]}"


def _initial_board() -> tuple[int, ...]:
    points = [0] * POINTS_COUNT
    points[23] = 2
    points[12] = 5
    points[7] = 3
    points[5] = 5
    points[0] = -2
    points[11] = -5
    points[16] = -3
    points[18] = -5
    return tuple(points)


def _roll_dice(rng) -> tuple[int, int]:
    return rng.randint(1, 6), rng.randint(1, 6)


def _legal_moves(state: BackgammonState) -> list[Move]:
    dice = _expanded_dice(state.dice)
    if not dice:
        return []

    sequences: list[Move] = []
    orders = [dice]
    if len(dice) == 2 and dice[0] != dice[1]:
        orders.append([dice[1], dice[0]])

    for order in orders:
        sequences.extend(_generate_sequences(state, order))

    if not sequences:
        return []

    unique_moves = list({move: move for move in sequences}.values())
    max_steps = max(len(move.steps) for move in unique_moves)
    if max_steps == 0:
        return []

    moves = [move for move in unique_moves if len(move.steps) == max_steps]

    if len(dice) == 2 and dice[0] != dice[1] and max_steps == 1:
        high = max(dice)
        high_moves = [move for move in moves if move.steps[0].die == high]
        if high_moves:
            moves = high_moves

    moves.sort(key=lambda move: move.notation())
    return moves


def _expanded_dice(dice: tuple[int, int]) -> list[int]:
    if dice[0] == dice[1]:
        return [dice[0]] * 4
    return [dice[0], dice[1]]


def _generate_sequences(state: BackgammonState, dice: Sequence[int]) -> list[Move]:
    sequences: list[Move] = []

    def recurse(
        current_state: BackgammonState, die_index: int, steps: list[Step]
    ) -> None:
        if die_index >= len(dice):
            sequences.append(Move(tuple(steps)))
            return
        die = dice[die_index]
        options = _legal_single_die_moves(current_state, die)
        if not options:
            sequences.append(Move(tuple(steps)))
            return
        for step in options:
            next_state = _apply_step(current_state, step)
            recurse(next_state, die_index + 1, steps + [step])

    recurse(state, 0, [])
    return sequences


def _apply_move(state: BackgammonState, move: Move, rng) -> BackgammonState:
    updated = state
    for step in move.steps:
        updated = _apply_step(updated, step)
    return _advance_turn(updated, rng)


def apply_move_with_dice(
    state: BackgammonState, move: Move, *, dice: tuple[int, int]
) -> BackgammonState:
    """Apply a move and advance the turn using explicit dice (AI helper)."""
    updated = state
    for step in move.steps:
        updated = _apply_step(updated, step)
    return advance_turn_with_dice(updated, dice=dice)


def _advance_turn(state: BackgammonState, rng) -> BackgammonState:
    return BackgammonState(
        points=state.points,
        active_color=state.active_color.opponent(),
        bar_white=state.bar_white,
        bar_black=state.bar_black,
        off_white=state.off_white,
        off_black=state.off_black,
        dice=_roll_dice(rng),
    )


def advance_turn_with_dice(
    state: BackgammonState, *, dice: tuple[int, int]
) -> BackgammonState:
    """Advance the turn and set dice explicitly (AI helper)."""
    return BackgammonState(
        points=state.points,
        active_color=state.active_color.opponent(),
        bar_white=state.bar_white,
        bar_black=state.bar_black,
        off_white=state.off_white,
        off_black=state.off_black,
        dice=dice,
    )


def _apply_step(state: BackgammonState, step: Step) -> BackgammonState:
    points = list(state.points)
    bar_white = state.bar_white
    bar_black = state.bar_black
    off_white = state.off_white
    off_black = state.off_black
    color = state.active_color
    sign = 1 if color is Color.WHITE else -1

    if step.start == BAR:
        if color is Color.WHITE:
            bar_white -= 1
        else:
            bar_black -= 1
    else:
        points[step.start] -= sign

    if step.end == OFF:
        if color is Color.WHITE:
            off_white += 1
        else:
            off_black += 1
    else:
        if points[step.end] == -sign:
            points[step.end] = 0
            if color is Color.WHITE:
                bar_black += 1
            else:
                bar_white += 1
        points[step.end] += sign

    return BackgammonState(
        points=tuple(points),
        active_color=color,
        bar_white=bar_white,
        bar_black=bar_black,
        off_white=off_white,
        off_black=off_black,
        dice=state.dice,
    )


def _legal_single_die_moves(state: BackgammonState, die: int) -> list[Step]:
    color = state.active_color
    points = state.points
    sign = 1 if color is Color.WHITE else -1
    moves: list[Step] = []

    bar_count = _bar_count(state, color)
    if bar_count > 0:
        dest = _entry_index(color, die)
        if _is_blocked(points, color, dest):
            return []
        hit = points[dest] == -sign
        moves.append(Step(BAR, dest, die, hit))
        return moves

    for idx, count in enumerate(points):
        if count * sign <= 0:
            continue
        dest = idx - die if color is Color.WHITE else idx + die
        if 0 <= dest < POINTS_COUNT:
            if _is_blocked(points, color, dest):
                continue
            hit = points[dest] == -sign
            moves.append(Step(idx, dest, die, hit))
            continue
        if _can_bear_off(state, color) and _can_bear_off_from(state, idx, dest):
            moves.append(Step(idx, OFF, die, False))

    return moves


def _bar_count(state: BackgammonState, color: Color) -> int:
    return state.bar_white if color is Color.WHITE else state.bar_black


def _can_bear_off(state: BackgammonState, color: Color) -> bool:
    if color is Color.WHITE:
        if state.bar_white > 0:
            return False
        return all(count <= 0 for count in state.points[6:])
    if state.bar_black > 0:
        return False
    return all(count >= 0 for count in state.points[:18])


def _can_bear_off_from(state: BackgammonState, idx: int, dest: int) -> bool:
    points = state.points
    color = state.active_color
    if color is Color.WHITE:
        if dest == -1:
            return True
        if dest < -1:
            return all(points[pos] <= 0 for pos in range(idx + 1, 6))
        return False
    if dest == 24:
        return True
    if dest > 24:
        return all(points[pos] >= 0 for pos in range(idx + 1, 24))
    return False


def _entry_index(color: Color, die: int) -> int:
    if color is Color.WHITE:
        return 24 - die
    return die - 1


def _is_blocked(points: Sequence[int], color: Color, dest: int) -> bool:
    sign = 1 if color is Color.WHITE else -1
    return points[dest] * sign <= -2


def _render_board(points: Sequence[int]) -> str:
    top_points = list(range(13, 25))
    bottom_points = list(range(12, 0, -1))
    top_cells = [_format_point(points[point - 1]) for point in top_points]
    bottom_cells = [_format_point(points[point - 1]) for point in bottom_points]

    top_grid = render_grid(
        [top_cells],
        row_labels=["Top"],
        col_labels=[str(point) for point in top_points],
        cell_width=3,
        padding=1,
    )
    bottom_grid = render_grid(
        [bottom_cells],
        row_labels=["Bottom"],
        col_labels=[str(point) for point in bottom_points],
        cell_width=3,
        padding=1,
    )
    return f"{top_grid}\n{bottom_grid}"


def _format_point(count: int) -> str:
    if count == 0:
        return "."
    color = "W" if count > 0 else "B"
    return f"{color}{abs(count)}"
