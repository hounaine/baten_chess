# rules.py

from copy import deepcopy
from typing import Tuple
from baten_chess_engine.board import Board


def opposite(color: str) -> str:
    """Return the opposite color ('w' <-> 'b')."""
    return 'w' if color == 'b' else 'b'


def square_attacked(cell: int, attacker_color: str, board: Board) -> bool:
    """
    Returns True if any piece of `attacker_color` can attack the specified `cell`.
    """
    for src, piece in board.pieces.items():
        if piece[0] != attacker_color:
            continue
        ptype = piece[1]
        df = (cell // 10) - (src // 10)
        dr = (cell % 10) - (src % 10)
        # Rook or Queen (straight lines)
        if ptype in ('R', 'Q') and (df == 0 or dr == 0):
            if board.path_clear(src, cell):
                return True
        # Bishop or Queen (diagonals)
        if ptype in ('B', 'Q') and abs(df) == abs(dr):
            if board.path_clear(src, cell):
                return True
        # Knight
        if ptype == 'N' and sorted([abs(df), abs(dr)]) == [1, 2]:
            return True
        # Pawn attacks
        direction = 1 if attacker_color == 'w' else -1
        if ptype == 'P' and dr == direction and abs(df) == 1:
            return True
        # King adjacent
        if ptype == 'K' and max(abs(df), abs(dr)) == 1:
            return True
    return False


def is_in_check(board: Board, color: str) -> bool:
    """
    Returns True if the king of `color` is in check.
    """
    kings = [c for c, p in board.pieces.items() if p == f"{color}K"]
    if not kings:
        return False
    king_cell = kings[0]
    return square_attacked(king_cell, opposite(color), board)


def castling_allowed(src: int, dst: int, board: Board) -> bool:
    """
    Checks if castling from `src` to `dst` is allowed by current rights.
    """
    color = board.pieces.get(src, '')[0]
    rights = board.castling_rights
    king_side = dst > src
    flag = ('K' if color == 'w' else 'k') if king_side else ('Q' if color == 'w' else 'q')
    if not rights.get(flag, False):
        return False
    step = 1 if king_side else -1
    path = [src + step, src + 2 * step]
    for square in path:
        if not board.is_empty(square):
            return False
        tmp = deepcopy(board)
        tmp.pieces.pop(src, None)
        tmp.pieces[square] = f"{color}K"
        if square_attacked(square, opposite(color), tmp):
            return False
    return True


def move_respects_pin(piece: str, src: int, dst: int, board: Board) -> bool:
    """
    Returns True if simulating the move does not leave own king in check.
    """
    color = piece[0]
    test_board = deepcopy(board)
    test_board.pieces.pop(dst, None)
    test_board.pieces[dst] = piece
    test_board.pieces.pop(src, None)
    test_board.last_move = board.last_move
    return not is_in_check(test_board, color)
