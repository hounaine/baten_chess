# tests/manual_mate.py
import copy
import pytest

from baten_chess_engine.board import Board
from baten_chess_engine.check_rules import generate_legal_moves
from baten_chess_engine.rules import is_in_check

def _make_move_and_copy(board, move):
    b2 = copy.deepcopy(board)
    piece, src, dst = move
    b2.apply_move(piece, src, dst)
    return b2

def test_mate_in_one_position():
    # FEN d’un mat en un (à adapter à votre position)
    fen = "4k3/8/8/8/3Q4/8/8/4K3 w - - 0 1"
    b = Board()
    b.load_fen(fen)

    # Générer tous les coups des Blancs
    legal_moves = generate_legal_moves(b, 'w')
    # Il doit en exister au moins un qui donne mat
    mates = [
        mv for mv in legal_moves
        if is_in_check(_make_move_and_copy(b, mv), 'b') and
           not generate_legal_moves(_make_move_and_copy(b, mv), 'b')
    ]
    assert mates, "Il doit y avoir un coup menant au mat en un coup"
