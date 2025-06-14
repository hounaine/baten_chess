# baten_chess_engine/rules.py

from copy import deepcopy
from typing import Optional, Tuple

from baten_chess_engine.core import Board


def opposite(color: str) -> str:
    return 'b' if color == 'w' else 'w'


def square_attacked(cell: int, attacker_color: str, board: Board) -> bool:
    """
    Retourne True si une pièce de attacker_color attaque la case `cell`,
    en ignorant toute obstruction (pour la détection de mat).
    """
    for src, piece in board.pieces.items():
        if piece[0] != attacker_color:
            continue
        ptype = piece[1]
        src_file, src_rank = divmod(src, 10)
        dst_file, dst_rank = divmod(cell, 10)
        df = dst_file - src_file
        dr = dst_rank - src_rank

        # Tours et Dames (lignes / colonnes)
        if ptype in ('R', 'Q') and (df == 0 or dr == 0):
            return True
        # Fous et Dames (diagonales)
        if ptype in ('B', 'Q') and abs(df) == abs(dr):
            return True
        # Cavaliers
        if ptype == 'N' and sorted((abs(df), abs(dr))) == [1, 2]:
            return True
        # Pions (attaque diagonale)
        direction = 1 if attacker_color == 'w' else -1
        if ptype == 'P' and dr == direction and abs(df) == 1:
            return True
        # Roi (une case autour)
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
    king_side = dst > src
    flag = (
        'K' if color == 'w' and king_side else
        'Q' if color == 'w' and not king_side else
        'k' if color == 'b' and king_side else
        'q'
    )
    if not board.castling_rights.get(flag, False):
        return False

    # s’assurer que les cases entre roi et tour sont vides et non attaquées
    step = 1 if king_side else -1
    path = [src + step, src + 2 * step]
    for sq in path:
        # 1) case vide ?
        if sq in board.pieces:
            return False
        # 2) case non attaquée ?
        tmp = deepcopy(board)
        tmp.pieces.pop(src)
        tmp.pieces[sq] = f'{color}K'
        if square_attacked(sq, opposite(color), tmp):
            return False



def move_respects_pin(piece: str, src: int, dst: int, board: Board) -> bool:
    """
    Retourne False si le coup expose le roi à un échec (auto-échec).
    Pour le roi, vérifie si la case d'arrivée est attaquée.
    Pour les autres pièces, simule le coup et vérifie si le roi est en échec.
    """
    if piece[1] == 'K':
        # Si on déplace le roi, il ne doit pas aller sur une case attaquée
        return not square_attacked(dst, opposite(piece[0]), board)
    else:
        tmp = deepcopy(board)
        # on fait « src→dst »
        tmp.pieces.pop(src, None)
        tmp.pieces[dst] = piece
        # on identifie la case du roi
        king_sq = next(sq for sq,p in tmp.pieces.items() if p == f'{piece[0]}K')
        # on regarde si, en respectant path_clear, un ennemi attaque ce roi
        for attacker_sq, attacker_piece in tmp.pieces.items():
            if attacker_piece[0] != opposite(piece[0]):
                continue
            ptype = attacker_piece[1]
            df = (king_sq//10) - (attacker_sq//10)
            dr = (king_sq%10) - (attacker_sq%10)
            # tour / dame
            if ptype in ('R','Q') and (df == 0 or dr == 0):
                if tmp.path_clear(attacker_sq, king_sq):
                    return False
            # fou / dame
            if ptype in ('B','Q') and abs(df) == abs(dr):
                if tmp.path_clear(attacker_sq, king_sq):
                    return False
            # cavalier
            if ptype == 'N' and sorted((abs(df),abs(dr))) == [1,2]:
                return False
            # pion
            direction = 1 if attacker_piece[0] == 'w' else -1
            if ptype == 'P' and dr == direction and abs(df) == 1:
                return False
            # roi (pour rare cas)
            if ptype == 'K' and max(abs(df),abs(dr)) == 1:
                return False
        # si aucune attaque valide n’a été trouvée, le coup lève bien le clou
        return True


def generate_legal_moves(board: Board, color: str):
    """
    Génère tous les coups légaux pour la couleur donnée.
    Retourne une liste de tuples (piece, src, dst).
    """
    from baten_chess_engine.core.move_validator import is_valid_move
    moves = []
    valid_cells = [file * 10 + rank for file in range(1, 9) for rank in range(1, 9)]
    for src, piece in board.pieces.items():
        if piece[0] != color:
            continue
        for dst in valid_cells:
            if src == dst:
                continue
            # Gestion spéciale du roque pour le roi
            if piece[1] == 'K' and abs(src - dst) == 2:
                from baten_chess_engine.core.rules import castling_allowed
                if castling_allowed(src, dst, board):
                    # Simule le roque pour vérifier l'auto-échec
                    import copy
                    test_board = copy.deepcopy(board)
                    test_board.apply_move(piece, src, dst)
                    if not is_in_check(test_board, color):
                        moves.append((piece, src, dst))
                continue
            if not board.is_empty(dst) and not board.is_enemy(dst, color):
                continue
            if is_valid_move(piece, src, dst, board, board.last_move):
                import copy
                test_board = copy.deepcopy(board)
                test_board.apply_move(piece, src, dst)
                if not is_in_check(test_board, color):
                    moves.append((piece, src, dst))
    return moves
