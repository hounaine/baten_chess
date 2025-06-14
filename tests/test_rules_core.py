import pytest
from baten_chess_engine.core.board import Board
from baten_chess_engine.core.rules import is_in_check, castling_allowed, move_respects_pin, opposite


@pytest.fixture
def empty_board():
    b = Board()
    b.load_fen("8/8/8/8/8/8/8/8 w - - 0 1")
    return b


# 1) Tests is_in_check

def test_check_by_rook(empty_board):
    # Roi blanc en e1 (51), tour noire en e8 (58)
    empty_board.pieces = {51: 'wK', 58: 'bR'}
    assert is_in_check(empty_board, 'w')

def test_check_by_bishop(empty_board):
    # Roi noir en d4 (44), fou blanc en g1 (71)
    empty_board.pieces = {44: 'bK', 71: 'wB'}
    assert is_in_check(empty_board, 'b')

def test_check_by_knight(empty_board):
    # Roi blanc en d4 (44), cavalier noir en c6 (63)
    empty_board.pieces = {44: 'wK', 63: 'bN'}
    assert is_in_check(empty_board, 'w')

def test_check_by_pawn(empty_board):
    # Pion noir en e5 (55) attaque roi blanc en d4 (44)
    empty_board.pieces = {44: 'wK', 55: 'bP'}
    assert is_in_check(empty_board, 'w')


# 2) Tests castling_allowed

def test_castling_allowed_simple(empty_board):
    # e1 (51) et h1 (54) vides, droits intacts
    empty_board.pieces = {51: 'wK', 54: 'wR'}
    empty_board.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
    assert castling_allowed(51, 53, empty_board)  # roque roi vers g1 (53)

def test_castling_blocked_by_piece(empty_board):
    # case f1 (52) occupée
    empty_board.pieces = {51: 'wK', 52: 'wB', 54: 'wR'}
    assert not castling_allowed(51, 53, empty_board)

def test_castling_blocked_by_attack(empty_board):
    # case f1 (52) attaquée par tour noire en b4 (24)
    empty_board.pieces = {51: 'wK', 54: 'wR', 24: 'bR'}
    assert not castling_allowed(51, 53, empty_board)


# 3) Tests move_respects_pin

def test_rook_pin_vertical(empty_board):
    # Roi blanc en e1 (51), tour noire en e8 (58) --> tour blanche en e2 (52) est clouée
    empty_board.pieces = {51: 'wK', 58: 'bR', 52: 'wR'}
    # déplacer la tour blanche de e2 (52) vers f2 (62) enlève la protection du roi
    assert not move_respects_pin('wR', 52, 62, empty_board)

def test_knight_not_pinned(empty_board):
    # même config, cavalier blanc en g1 (71) n’est pas cloué
    empty_board.pieces = {51: 'wK', 58: 'bR', 71: 'wN'}
    assert move_respects_pin('wN', 71, 52, empty_board)  # cavalier de g1 vers e2 permis

def test_pin_diagonal(empty_board):
    # Roi blanc en d1 (41), fou noir en a4 (14), cavalier blanc en c2 (32) est cloué
    empty_board.pieces = {41: 'wK', 14: 'bB', 32: 'wN'}
    # cavalier ne peut pas bouger hors de la diagonale
    assert not move_respects_pin('wN', 32, 54, empty_board)  # c2→e4 brise le clouage
