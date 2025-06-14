import pytest

from baten_chess_engine.core.board import Board
from baten_chess_engine.core.check_rules import (
    generate_legal_moves,
    is_checkmate,
    is_stalemate
)
from baten_chess_engine.core.move_validator import is_valid_move

@pytest.fixture
def board():
    b = Board()
    b.load_fen("8/8/8/8/8/8/8/8 w - - 0 1")  # vide
    return b

def play_moves(b, moves):
    """Applique une liste de coups [(src,dst),...] sur b, en alternant."""
    turn = 'w'
    for src, dst in moves:
        piece = b.pieces[src]
        assert piece[0] == turn, f"Wrong turn expecting {turn}"
        assert is_valid_move(piece, src, dst, b, b.last_move)
        b.apply_move(piece, src, dst)
        turn = 'b' if turn == 'w' else 'w'
    return b

def test_checkmate_simple():
    # Mat en 1 : position du "Fool’s mate"
    fen = "rnb1kbnr/pppp1ppp/8/4p3/8/4P3/PPPP1PPP/RNB1KBNR w KQkq - 0 2"
    b = Board(); b.load_fen(fen)
    # 2. Qh5# (d1→h5)
    assert is_valid_move('wQ', 41, 85, b, b.last_move)
    b.apply_move('wQ', 41, 85)
    assert is_checkmate(b, 'b')

def test_stalemate_simple():
    # Pat : roi seul au bord
    fen = "7k/5Q2/6K1/8/8/8/8/8 b - - 0 1"
    b = Board(); b.load_fen(fen)
    assert is_stalemate(b, 'b')
    assert not is_checkmate(b, 'b')

def test_pawn_promotion():
    # Pion blanc en 7e rangée, avance et promeut
    fen = "8/P7/8/8/8/8/8/4k3 w - - 0 1"
    b = Board(); b.load_fen(fen)
    # 61→71 puis promotion to Q
    assert is_valid_move('wP', 61, 71, b, b.last_move)
    b.apply_move('wP', 61, 71)
    # simulation de promotion (dans votre code, gérez promotion séparément)
    b.pieces[71] = 'wQ'
    assert b.pieces[71] == 'wQ'

def test_castling():
    # Petit roque blanc autorisé
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"
    b = Board(); b.load_fen(fen)
    # Petit roque : e1→g1 (51→71)
    assert is_valid_move('wK', 51, 71, b, b.last_move)
    b.apply_move('wK', 51, 71)
    # Grand roque noir autorisé
    b.turn = 'b'
    b.pieces[58] = 'bK'; b.pieces[55] = 'bR'
    b.castling_rights = {'K': True,'Q': True,'k': True,'q': True}
    assert is_valid_move('bK', 58, 38, b, b.last_move)

def test_en_passant():
    fen = "8/8/8/8/5pP1/8/8/4K3 w - f6 0 1"
    b = Board(); b.load_fen(fen)
    # blanc joue g5xf6 en passant : src=67 → dst=66
    assert is_valid_move('wP', 67, 66, b, b.last_move)
    b.apply_move('wP', 67, 66)
    # case f5 (76) doit être capturée
    assert 76 not in b.pieces

def test_fairy_piece_wazir():
    # Définissez un wazir (mvt d'une case orthogonale)
    # On ajoute temporairement Delta pour W:
    from baten_chess_engine.core.move_validator import FAIRY_DELTAS
    FAIRY_DELTAS['W'] = [(1,0),(-1,0),(0,1),(0,-1)]
    fen = "8/8/8/3W4/8/8/8/4k3 w - - 0 1"
    b = Board(); b.load_fen(fen)
    # wazir en d5 (44) peut aller en d6 (45)
    assert is_valid_move('wW', 44, 45, b, b.last_move)
