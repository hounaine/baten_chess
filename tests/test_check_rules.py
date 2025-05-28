# tests/test_check_rules.py

import copy
import pytest

from baten_chess_engine.check_rules import is_checkmate, is_stalemate, generate_legal_moves
from baten_chess_engine.board import Board
from baten_chess_engine.rules import is_in_check

def test_initial_position_has_moves():
    board = Board()
    board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    # White to move
    board.turn = 'w'
    moves_white = generate_legal_moves(board, 'w')
    assert len(moves_white) > 0, "White doit avoir des coups en position initiale"
    # Black to move
    board.turn = 'b'
    moves_black = generate_legal_moves(board, 'b')
    assert len(moves_black) > 0, "Black doit avoir des coups en position initiale"

def test_simple_check_not_checkmate():
    # Position : roi blanc en e1 (51), tour noire en e8 (58)
    board = Board()
    board.pieces = {51: 'wK', 58: 'bR'}
    board.turn = 'w'
    board.last_move = None
    assert is_in_check(board, 'w'), "Le roi blanc doit être en échec"
    assert not is_checkmate(board, 'w'), "Ce n'est pas échec et mat, il y a des issues possibles"

def test_checkmate_position():
    # Position de mat : roi noir en a8 (18), dame blanche en b7 (27), roi blanc en c6 (36)
    board = Board()
    board.pieces = {18: 'bK', 27: 'wQ', 36: 'wK'}
    board.turn = 'b'
    board.last_move = None
    assert is_in_check(board, 'b'), "Le roi noir doit être en échec"
    assert is_checkmate(board, 'b'), "C'est bien échec et mat pour le noir"

def test_stalemate_position():
    # Position de pat : roi noir en a8 (18), dame blanche en b6 (26), roi blanc en c7 (37)
    board = Board()
    board.pieces = {18: 'bK', 26: 'wQ', 37: 'wK'}
    board.turn = 'b'
    board.last_move = None
    assert not is_in_check(board, 'b'), "Le roi noir ne doit pas être en échec"
    assert is_stalemate(board, 'b'), "C'est bien une position de pat pour le noir"
