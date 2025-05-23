# baten_chess_engine/validator_dsl.py

"""
validator_dsl.py

Validation des coups générée à partir du DSL (ici pour la tour et le cavalier).
"""

from typing import Optional, Tuple
from baten_chess_engine.board import Board

# Ensembles pour les différences et deltas
ROOK_DIFFS     = set(range(1, 8)) | {10 * i for i in range(1, 8)}
KNIGHT_DELTAS  = {(1, 2), (2, 1)}  # (Δcol, Δligne)

def is_valid_rook_move(piece: str, src: int, dst: int, state: Board) -> bool:
    """Valide un coup de tour (R)."""
    if len(piece) != 2 or piece[1] != 'R':
        return False
    color = piece[0]
    if color != state.turn:
        return False
    diff = abs(src - dst)
    if diff not in ROOK_DIFFS:
        return False
    if not state.path_clear(src, dst):
        return False
    if not (state.is_empty(dst) or state.is_enemy(dst, color)):
        return False
    return True

def is_valid_knight_move(piece: str, src: int, dst: int, state: Board) -> bool:
    """Valide un coup de cavalier (N)."""
    if len(piece) != 2 or piece[1] != 'N':
        return False
    color = piece[0]
    if color != state.turn:
        return False
    c1, l1 = divmod(src, 10)
    c2, l2 = divmod(dst, 10)
    if (abs(c1 - c2), abs(l1 - l2)) not in KNIGHT_DELTAS:
        return False
    if not (state.is_empty(dst) or state.is_enemy(dst, color)):
        return False
    return True

def is_valid_move_dsl(piece: str,
                      src: int,
                      dst: int,
                      state: Board,
                      last_move: Optional[Tuple[int,int]] = None) -> bool:
    """
    Point d’entrée unique pour la validation via DSL.
    Pour l’instant, traite :
      - la tour (R),
      - le cavalier (N).
    """
    if piece[1] == 'R':
        return is_valid_rook_move(piece, src, dst, state)
    if piece[1] == 'N':
        return is_valid_knight_move(piece, src, dst, state)
    # TODO: ajouter is_valid_pawn_move, is_valid_bishop_move, etc.
    return False
