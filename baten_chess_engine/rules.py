# rules.py — rule engine for Baten Chess

from typing import Tuple, Set, Dict
from baten_chess_engine.board import Board
from baten_chess_engine.validator_dsl import (
    is_valid_rook_move, is_valid_knight_move,
    is_valid_bishop_move, is_valid_queen_move,
    is_valid_pawn_move, is_valid_king_move
)

def opposite(color: str) -> str:
    """Return the other color: 'w'→'b', 'b'→'w'."""
    return 'b' if color == 'w' else 'w'

def square_attacked(cell: int, attacker_color: str, board: Board) -> bool:
    """
    True if any enemy piece of color `attacker_color` can move to `cell`
    ignoring checks. Uses pure cinématique + path_clear.
    """
    for src, piece in board.pieces.items():
        if piece[0] != attacker_color:
            continue
        ptype = piece[1]
        # dispatch to validator_dsl
        ok = False
        if ptype == 'R':
            ok = is_valid_rook_move(piece, src, cell, board)
        elif ptype == 'N':
            ok = is_valid_knight_move(piece, src, cell, board)
        elif ptype == 'B':
            ok = is_valid_bishop_move(piece, src, cell, board)
        elif ptype == 'Q':
            ok = is_valid_queen_move(piece, src, cell, board)
        elif ptype == 'K':
            ok = is_valid_king_move(piece, src, cell, board)
        elif ptype == 'P':
            # pawns attack only diagonally
            # reuse is_valid_pawn_move but ensure dst==cell and it's a capture
            ok = is_valid_pawn_move(piece, src, cell, board) and src//10 != cell//10
        if ok:
            return True
    return False

def is_in_check(board: Board, color: str) -> bool:
    """
    True if `color`'s king is under attack.
    """
    # find king
    kings = [c for c,p in board.pieces.items() if p == f'{color}K']
    if not kings:
        return False
    king_cell = kings[0]
    return square_attacked(king_cell, opposite(color), board)

def castling_allowed(src: int, dst: int, board: Board) -> bool:
    """
    Check castling rights:
     - king/rook haven’t moved (castling_rights)
     - no pieces between src and dst
     - king not in, through, or into check
    """
    color = board.pieces[src][0]
    rights = board.castling_rights
    # determine side
    king_side = dst > src
    flag = 'K' if color=='w' and king_side else \
           'Q' if color=='w' and not king_side else \
           'k' if color=='b' and king_side else 'q'
    if not rights.get(flag, False):
        return False

    # squares the king crosses
    step = 1 if king_side else -1
    path = [src + step, src + 2*step]
    # ensure path_clear and not attacked
    for sq in path:
        if not board.is_empty(sq):
            return False
        # simulate king on intermediate square
        tmp = board.pieces.pop(src)
        board.pieces[sq] = f'{color}K'
        attacked = square_attacked(sq, opposite(color), board)
        # revert
        board.pieces[src] = tmp
        board.pieces.pop(sq)
        if attacked:
            return False
    return True

def move_respects_pin(piece: str, src: int, dst: int, board: Board) -> bool:
    """
    True if moving `piece` src→dst does not expose own king to check
    due to a pin.
    """
    color = piece[0]
    # simulate move
    tmp = board.pieces.pop(src)
    captured = board.pieces.pop(dst, None)
    board.pieces[dst] = tmp

    pinned = is_in_check(board, color)

    # revert
    board.pieces[src] = tmp
    if captured: board.pieces[dst] = captured
    else:        board.pieces.pop(dst)

    return not pinned

def is_move_legal(
    piece: str, src: int, dst: int, board: Board,
    last_move: Tuple[int,int] = None
) -> bool:
    """
    Full move legality:
      1) correct turn
      2) target empty or enemy (captures)
      3) pure cinématique
      4) simulate + no check
      5) king specific (no into check, castling)
      6) en-passant capture
      7) promotion spot
      8) pin
    """
    color = piece[0]
    # 1) turn
    if color != board.turn:
        return False

    # 2) destination must be empty or enemy (except en-passant)
    if dst in board.pieces and board.pieces[dst][0] == color:
        return False

    # 3) pure movement
    from baten_chess_engine.validator_dsl import is_valid_move_dsl
    if not is_valid_move_dsl(piece, src, dst, board, last_move):
        return False

    # 4) simulate full move
    import copy
    new = copy.deepcopy(board)
    new.pieces.pop(dst, None)
    new.pieces[dst] = piece
    new.pieces.pop(src, None)
    new.last_move = last_move

    # 5) no self-check
    if is_in_check(new, color):
        return False

    # 6) handle castling
    if piece[1]=='K' and abs(src-dst)==2:
        if not castling_allowed(src, dst, board):
            return False

    # 7) handle en-passant
    if piece[1]=='P' and dst == board.en_passant_target:
        # remove the captured pawn
        cap = (dst//10 + (-1 if color=='w' else +1))*10 + dst%10
        if cap in board.pieces and board.pieces[cap][0] != color:
            new.pieces.pop(cap, None)

    # 8) handle promotion (done at state update, not here)

    # 9) pin
    if not move_respects_pin(piece, src, dst, board):
        return False

    return True
