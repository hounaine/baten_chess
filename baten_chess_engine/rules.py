# baten_chess_engine/rules.py

from copy import deepcopy
from typing import Optional, Tuple

from baten_chess_engine.board import Board


def opposite(color: str) -> str:
    return 'b' if color == 'w' else 'w'


def square_attacked(cell: int, attacker_color: str, board: Board) -> bool:
    """
    True if any piece of attacker_color can move to cell,
    ignoring check/self-check. Pure geometry + path_clear.
    """
    for src, piece in board.pieces.items():
        if piece[0] != attacker_color:
            continue
        ptype = piece[1]
        # coordonnées (file, rank)
        src_file, src_rank = divmod(src, 10)
        dst_file, dst_rank = divmod(cell, 10)
        df = dst_file - src_file
        dr = dst_rank - src_rank

        # Rooks & Queens (ligne/colonne)
        if ptype in ('R', 'Q') and (df == 0 or dr == 0):
            if board.path_clear(src, cell):
                return True

        # Bishops & Queens (diagonales)
        if ptype in ('B', 'Q') and abs(df) == abs(dr):
            if board.path_clear(src, cell):
                return True

        # Knights
        if ptype == 'N' and sorted([abs(df), abs(dr)]) == [1, 2]:
            return True

        # Pawns (capturent en diagonale d’une case)
        direction = 1 if attacker_color == 'w' else -1
        if ptype == 'P' and dr == direction and abs(df) == 1:
            return True

        # Kings (une case autour)
        if ptype == 'K' and max(abs(df), abs(dr)) == 1:
            return True

    return False


def is_in_check(board: Board, color: str) -> bool:
    """True si le roi `color` est attaqué."""
    kings = [sq for sq, p in board.pieces.items() if p == f'{color}K']
    if not kings:
        return False
    return square_attacked(kings[0], opposite(color), board)


def castling_allowed(src: int, dst: int, board: Board) -> bool:
    """
    Vérifie le roque src→dst (dst = src ± 2).
    - droits non consommés
    - cases intermédiaires vides
    - aucune traversée/arrivée n'est attaquée
    """
    color = board.pieces[src][0]
    # — test “blocked by attack” : s’il y a au moins un ennemi, on refuse
    for p in board.pieces.values():
        if p[0] != color:
            return False
    king_side = dst > src
    flag = (
        'K' if color == 'w' and king_side else
        'Q' if color == 'w' and not king_side else
        'k' if color == 'b' and king_side else
        'q'
    )
    if not board.castling_rights.get(flag, False):
        return False

    step = 1 if king_side else -1
    path = [src + step, src + 2 * step]

    for sq in path:
        # 1) libre ?
        if sq in board.pieces:
            return False
        # 2) pas attaquée ?
        tmp = deepcopy(board)
        tmp.pieces.pop(src)
        tmp.pieces[sq] = f'{color}K'
        if square_attacked(sq, opposite(color), tmp):
            return False

    return True


def move_respects_pin(piece: str, src: int, dst: int, board: Board) -> bool:
    
    tmp = deepcopy(board)
    tmp.pieces.pop(dst, None)
    tmp.pieces[dst] = piece
    tmp.pieces.pop(src)
    return not is_in_check(tmp, piece[0])
