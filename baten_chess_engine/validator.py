# baten_chess_engine/validator.py

from typing import Optional, Tuple
from .board import Board

# Différences absolues pour les pièces coulissantes et le roi
KING_DIFFS   = {1, 9, 10, 11}
BISHOP_DIFFS = {9*i for i in range(1,8)} | {11*i for i in range(1,8)}
ROOK_DIFFS   = set(range(1,8)) | {10*i for i in range(1,8)}
QUEEN_DIFFS  = BISHOP_DIFFS | ROOK_DIFFS

# Pions : avancées et captures
PAWN_MOVE = {10, 20}  # vertical 1-case (10) ou 2-cases (20)
PAWN_CAP  = {9, 11}   # captures diagonales

# Cavaliers : (Δcol, Δligne) = (1,2) ou (2,1)
KNIGHT_DELTAS = {(1,2), (2,1)}

ALLOWED_DIFFS = {
    'K': KING_DIFFS,
    'B': BISHOP_DIFFS,
    'R': ROOK_DIFFS,
    'Q': QUEEN_DIFFS,
}

def is_valid_move(piece: str,
                  src: int,
                  dst: int,
                  board: Board,
                  last_move: Optional[Tuple[int,int]] = None) -> bool:
    color, ptype = piece[0], piece[1]

    # 0) Trait
    if color != board.turn:
        return False

    # 1) Cavaliers
    if ptype == 'N':
        src_C, src_L = divmod(src, 10)
        dst_C, dst_L = divmod(dst, 10)
        dc, dr = abs(dst_C - src_C), abs(dst_L - src_L)
        if (dc, dr) not in KNIGHT_DELTAS:
            return False
        if not (board.is_empty(dst) or board.is_enemy(dst, color)):
            return False
        return True

    diff = abs(src - dst)

    # 2) Roque
    if ptype == 'K' and diff == 2 and is_castle_move(src, dst, board, color):
        return True

    # 3) Prise en passant
    if ptype == 'P' and last_move and board.en_passant_target == dst:
        lm_src, lm_dst = last_move
        if abs(lm_src - lm_dst) == 20 and diff in PAWN_CAP:
            return True

    # 4) Pions – traitements précis
    if ptype == 'P':
        # avancer d'une case
        if diff == 10 and board.is_empty(dst):
            return True
        # double-pas initial
        rank = src % 10
        if (diff == 20 and board.is_empty(dst)
            and ((color == 'w' and rank == 2) or (color == 'b' and rank == 7))):
            return True
        # capture diagonale
        if diff in PAWN_CAP and board.is_enemy(dst, color):
            return True
        return False

    # 5) Autres pièces (roi, fou, tour, dame)
    #   - test de base sur |src−dst|
    if diff not in ALLOWED_DIFFS.get(ptype, set()):
        return False
    #   - trajectoire libre pour fou, tour, dame
    if ptype in {'B','R','Q'} and not board.path_clear(src, dst):
        return False
    #   - case d’arrivée libre ou ennemie
    if not (board.is_empty(dst) or board.is_enemy(dst, color)):
        return False

    return True

def is_castle_move(src: int, dst: int, board: Board, color: str) -> bool:
    diff = dst - src
    side = ('K' if diff > 0 else 'Q') if color == 'w' else ('k' if diff > 0 else 'q')
    return board.castling_rights.get(side, False)
