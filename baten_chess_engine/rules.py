# baten_chess_engine/rules.py

from typing import Tuple
from baten_chess_engine.board import Board
from baten_chess_engine.validator_dsl import is_valid_move_dsl

def opposite(color: str) -> str:
    return 'w' if color == 'b' else 'b'

def is_in_check(board: Board, color: str) -> bool:
    """True si le roi de la couleur color est attaqué."""
    # trouve la position du roi
    king_pos = next((c for c,p in board.pieces.items() if p == f"{color}K"), None)
    if king_pos is None:
        return False
    # toute pièce ennemie qui peut bouger sur king_pos
    for src, p in board.pieces.items():
        if p[0] != color:
            if is_valid_move_dsl(p, src, king_pos, board):
                return True
    return False

def square_attacked(cell: int, by_color: str, board: Board) -> bool:
    """True si cell est attaquée par une pièce de by_color."""
    for src, p in board.pieces.items():
        if p[0] == by_color:
            if is_valid_move_dsl(p, src, cell, board):
                return True
    return False

def move_respects_pin(piece: str, src: int, dst: int, board: Board) -> bool:
    """
    Empêche une pièce clouée de bouger sauf pour capturer l’attaquant.
    """
    color = piece[0]
    # position du roi en amont
    king_pos = next((c for c,p in board.pieces.items() if p == f"{color}K"), None)
    if king_pos is None or piece[1] == 'K':
        return True

    # simule la pièce en levée de src
    captured = board.pieces.pop(dst, None)
    board.pieces[dst] = piece
    board.pieces.pop(src, None)

    pinned = square_attacked(king_pos, opposite(color), board)

    # restaure
    board.pieces[src] = piece
    if captured:
        board.pieces[dst] = captured
    else:
        board.pieces.pop(dst)

    # si cloué et qu’il ne capture pas l’attaquant direct → interdit
    if pinned:
        # si dst n’est pas situé sur la même ligne/col/diag de l’attaquant, on interdit
        attacker_pos = next((s for s,p in board.pieces.items()
                             if p[0] != color and is_valid_move_dsl(p, s, king_pos, board)), None)
        return dst == attacker_pos

    return True

def castling_allowed(src: int, dst: int, board: Board) -> bool:
    """
    Vérifie les conditions de roque (intermédiaires libres et non attaquées).
    src→dst = 2 cases pour le roi
    """
    color = board.pieces[src][0]
    # détermination king/queen side
    if color == 'w':
        rank = 1
        enemy = 'b'
    else:
        rank = 8
        enemy = 'w'
    # cases traversées
    step = 1 if dst > src else -1
    pos = src
    # le roi ne doit pas être en échec initial
    if is_in_check(board, color):
        return False
    while pos != dst:
        pos += step
        # chaque case ne doit pas être attaquée
        if square_attacked(pos, enemy, board):
            return False
    return True
