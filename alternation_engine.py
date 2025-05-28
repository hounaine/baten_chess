"""
alternation_engine.py

Module to manage turn alternation logic for various chess variants,
including placement, game phase, number of moves per player, etc.
"""

from typing import Callable, List


class MoveContext:
    """Encapsulates information about a move for alternation decisions."""
    def __init__(self, move, is_capture: bool = False, is_end_of_sequence: bool = False):
        self.move = move
        self.is_capture = is_capture
        self.is_end_of_sequence = is_end_of_sequence
        # Additional flags can be added for future variants.


class TurnRule:
    """Abstract base class for turn-switching rules."""
    def should_switch(self, ctx: MoveContext) -> bool:
        raise NotImplementedError("TurnRule.should_switch must be implemented by subclasses")


class StrictAlternate(TurnRule):
    """Switch turn after every move."""
    def should_switch(self, ctx: MoveContext) -> bool:
        return True


class NeverAlternate(TurnRule):
    """Never switch turn (e.g., placement phase)."""
    def should_switch(self, ctx: MoveContext) -> bool:
        return False


class AlternateOnCapture(TurnRule):
    """Switch turn only on capture."""
    def should_switch(self, ctx: MoveContext) -> bool:
        return ctx.is_capture


class AlternateOnLastSequence(TurnRule):
    """Switch turn at the last move of a sequence (féerique variant)."""
    def should_switch(self, ctx: MoveContext) -> bool:
        return ctx.is_end_of_sequence


class Phase:
    """Defines a phase with its own turn rule and transition condition."""
    def __init__(self, name: str, turn_rule: TurnRule, transition_condition: Callable[[MoveContext], bool]):
        self.name = name
        self.turn_rule = turn_rule
        self.transition_condition = transition_condition


class AlternationEngine:
    """Engine to manage phases and turn alternation across game variants."""
    def __init__(self, phases: List[Phase], initial_turn: str = 'w'):
        self.phases = phases
        self.current_phase = phases[0] if phases else None
        self.turn = initial_turn

    def register_move(self, ctx: MoveContext):
        """
        Update phase and turn based on the move context.
        """
        # Phase transition
        if self.current_phase and self.current_phase.transition_condition(ctx):
            idx = self.phases.index(self.current_phase)
            if idx + 1 < len(self.phases):
                self.current_phase = self.phases[idx + 1]

        # Turn switching
        if self.current_phase and self.current_phase.turn_rule.should_switch(ctx):
            self.turn = 'b' if self.turn == 'w' else 'w'

    def get_current_turn(self) -> str:
        """Return the current player's turn (e.g., 'w' or 'b')."""
        return self.turn
