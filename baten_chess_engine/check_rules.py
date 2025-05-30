"""
check_rules.py

Module dedicated to detection of check and checkmate conditions.
"""
from typing import List, Tuple
import copy

from baten_chess_engine.board import Board
from baten_chess_engine.move_validator import is_valid_move
from baten_chess_engine.rules import is_in_check, move_respects_pin, castling_allowed, opposite

# A move is represented as a tuple: (piece: str, src: int, dst: int)
Move = Tuple[str, int, int]


def generate_legal_moves(board: Board, player: str) -> List[Move]:
    """
    Generate all legal moves for a given player, taking into account
    movement rules, path obstructions, pins, and king safety.
    """
    legal_moves: List[Move] = []
    all_cells = [file * 10 + rank for file in range(1, 9) for rank in range(1, 9)]
    # Iterate over a snapshot of pieces to avoid mutation issues
    for src, piece in list(board.pieces.items()):
        if piece[0] != player:
            continue
        for dst in all_cells:
            if src == dst:
                continue
            # 1) Pure movement validation
            if not is_valid_move(piece, src, dst, board, board.last_move):
                continue
            # 2) Path clearance
            if not board.path_clear(src, dst):
                continue
            # 3) Pin check on a copy
            tmp_board = copy.deepcopy(board)
            if not move_respects_pin(piece, src, dst, tmp_board):
                continue
            # 4) King safety (no self-check)
            test_board = copy.deepcopy(board)
            test_board.apply_move(piece, src, dst)
            if is_in_check(test_board, player):
                continue
            # 5) Castling rights if king moves two squares
            if piece[1] == 'K' and abs(src - dst) == 2:
                if not castling_allowed(src, dst, board):
                    continue
            legal_moves.append((piece, src, dst))
    return legal_moves


def is_checkmate(board: Board, player: str) -> bool:
    """
    Determine if the given player is in checkmate.
    Returns True if in check and no legal moves exist.
    """
    if not is_in_check(board, player):
        return False
    moves = generate_legal_moves(board, player)
    return len(moves) == 0


def is_stalemate(board: Board, player: str) -> bool:
    """
    Determine if the given player is in stalemate.
    Returns True if not in check and no legal moves exist.
    """
    if is_in_check(board, player):
        return False
    moves = generate_legal_moves(board, player)
    return len(moves) == 0
