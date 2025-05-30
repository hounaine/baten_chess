import copy
import pytest

from baten_chess_engine.board import Board
from baten_chess_engine.rules import is_in_check, castling_allowed, move_respects_pin

def make_board(pieces):
    b = Board()
    b.pieces = pieces.copy()
    b.castling_rights = {'K': True,'Q': True,'k': True,'q': True}
    b.en_passant_target = None
    b.turn = 'w'
    b.last_move = None
    return b

def test_is_in_check_rook():
    # Roi blanc en e1 (51), tour noire en e8 (58)
    b = make_board({51:'wK', 58:'bR'})
    assert is_in_check(b, 'w')

def test_is_in_check_knight_and_pawn():
    # Cavalier noir en g3 (73) échec roi blanc en e2 (52)
    b = make_board({52:'wK', 73:'bN'})
    assert is_in_check(b, 'w')
    # Pion blanc en d4 (44) attaque roi noir en e5 (55)
    b = make_board({55:'bK', 44:'wP'})
    assert is_in_check(b, 'b')

def test_castling_blocked_by_attack_or_piece():
    # Montage initial : échec en f1 bloque roque roi blanc
    b = make_board({51:'wK', 61:'wR', 28:'bR'})  # tour noire en b8 attaquant f1 (61)
    assert not castling_allowed(51, 53, b)  # roi blanc tente g1
    
    # Chemin obstrué par une pièce
    b = make_board({51:'wK', 52:'wB', 61:'wR'})
    assert not castling_allowed(51, 53, b)

def test_castling_allowed_simple():
    # Plateau vide entre e1 (51) et h1 (54)
    b = make_board({51:'wK', 54:'wR'})
    # Pas d’attaque sur f1(52) ni g1(53)
    b.castling_rights['K'] = True
    assert castling_allowed(51, 53, b)

def test_move_respects_pin():
    # Clouage : roi blanc en e1 (51), tour blanche en a1 (11), tour noire en e8 (58)
    b = make_board({51:'wK', 11:'wR', 58:'bR'})
    # La tour blanche ne peut pas bouger, elle cloue le roi
    assert not move_respects_pin('wR', 11, 13, b)  # a1→c1

    # Déplacement du cavalier blanc en g1 (71) ne cloue pas
    b = make_board({51:'wK', 71:'wN', 58:'bR'})
    assert move_respects_pin('wN', 71, 52, b)  # g1→e2

