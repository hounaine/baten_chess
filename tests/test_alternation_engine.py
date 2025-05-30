import pytest
from alternation_engine import (
    AlternationEngine, Phase, NeverAlternate,
    StrictAlternate, AlternateOnCapture, MoveContext
)

def make_phase(rule, transition=lambda ctx: False):
    return Phase("test", rule, transition)

def test_strict_alternate():
    engine = AlternationEngine([make_phase(StrictAlternate())], initial_turn='w')
    ctx = MoveContext(move=('wP', 11, 21), is_capture=False)
    engine.register_move(ctx)
    assert engine.get_current_turn() == 'b'
    engine.register_move(ctx)
    assert engine.get_current_turn() == 'w'

def test_never_alternate():
    engine = AlternationEngine([make_phase(NeverAlternate())], initial_turn='w')
    ctx = MoveContext(move=('wP', 11, 21), is_capture=False)
    engine.register_move(ctx)
    assert engine.get_current_turn() == 'w'

def test_alternate_on_capture():
    phase = make_phase(AlternateOnCapture())
    engine = AlternationEngine([phase], initial_turn='w')
    ctx1 = MoveContext(move=('wP', 11, 21), is_capture=False)
    engine.register_move(ctx1)
    assert engine.get_current_turn() == 'w'
    ctx2 = MoveContext(move=('wP', 21, 31), is_capture=True)
    engine.register_move(ctx2)
    assert engine.get_current_turn() == 'b'

def test_phase_transition_and_alternation():
    # phase 1: NeverAlternate until a capture, then switch to StrictAlternate
    phases = [
        Phase('placement', NeverAlternate(), lambda ctx: ctx.is_capture),
        Phase('battle', StrictAlternate(), lambda ctx: False),
    ]
    engine = AlternationEngine(phases, initial_turn='w')
    # placement non-capture → stay in placement, no switch
    ctx = MoveContext(move=('wP', 11, 12), is_capture=False)
    engine.register_move(ctx)
    assert engine.current_phase.name == 'placement'
    assert engine.get_current_turn() == 'w'
    # placement capture → transition to battle and then switch turn
    ctx = MoveContext(move=('wP', 21, 31), is_capture=True)
    engine.register_move(ctx)
    assert engine.current_phase.name == 'battle'
    assert engine.get_current_turn() == 'b'
