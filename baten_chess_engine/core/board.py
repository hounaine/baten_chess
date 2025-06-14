# Updated baten_chess_engine/core/board.py

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, FrozenSet
import logging

@dataclass
class Board:
    pieces: Dict[int, str] = field(default_factory=dict)
    castling_rights: Dict[str, bool] = field(default_factory=lambda: {
        'K': True, 'Q': True, 'k': True, 'q': True
    })
    en_passant_target: Optional[int] = None
    turn: str = 'w'
    last_move: Optional[Tuple[int, int]] = None
    last_move_was_capture: bool = False
    history: List[Tuple[FrozenSet[Tuple[int,str]], Tuple[Tuple[str,bool],...], Optional[int], str]] = field(default_factory=list)
    game_over: bool = False

    def record_state(self):
        pieces_fs = frozenset(self.pieces.items())
        cr_tuple = tuple(sorted(self.castling_rights.items()))
        self.history.append((pieces_fs, cr_tuple, self.en_passant_target, self.turn))

    def load_fen(self, fen: str):
        rows = fen.split()[0].split('/')
        self.pieces.clear()
        rank = 8
        for row in rows:
            file = 1
            for ch in row:
                if ch.isdigit():
                    file += int(ch)
                else:
                    color = 'w' if ch.isupper() else 'b'
                    ptype = ch.upper()
                    cell = file * 10 + rank
                    self.pieces[cell] = color + ptype
                    file += 1
            rank -= 1
        self.en_passant_target = None
        self.turn = 'w'
        self.last_move = None
        self.last_move_was_capture = False
        self.game_over = False

    def is_empty(self, cell: int) -> bool:
        return cell not in self.pieces

    def is_enemy(self, cell: int, color: str) -> bool:
        p = self.pieces.get(cell)
        return bool(p and p[0] != color)

    def path_clear(self, src: int, dst: int) -> bool:
        src_file, src_rank = divmod(src, 10)
        dst_file, dst_rank = divmod(dst, 10)
        df = dst_file - src_file
        dr = dst_rank - src_rank
        step_file = (df > 0) - (df < 0)
        step_rank = (dr > 0) - (dr < 0)
        step = step_file * 10 + step_rank
        if not (df == 0 or dr == 0 or abs(df) == abs(dr)):
            return True
        pos = src + step
        while pos != dst:
            if pos in self.pieces:
                return False
            pos += step
        return True

    def apply_move(self, piece: str, src: int, dst: int):
        prev_enp = self.en_passant_target
        self.en_passant_target = None
        if piece[1] == 'P' and abs(src - dst) == 20:
            self.en_passant_target = (src + dst) // 2
        was_capture = False
        if dst in self.pieces:
            was_capture = True
        if piece[1] == 'P' and dst == prev_enp and self.last_move:
            lm_src, lm_dst = self.last_move
            if lm_dst in self.pieces:
                was_capture = True
                del self.pieces[lm_dst]
        if dst in self.pieces and not was_capture:
            del self.pieces[dst]
        # promotion automatique en dame si on atteint la dernière rangée
        rank = dst % 10
        if piece[1] == "P" and (rank == 8 or rank == 1):
            self.pieces[dst] = piece[0] + "Q"
        else:
            self.pieces[dst] = piece  # Toujours placer la pièce sur dst
        self.pieces.pop(src, None)
        self.last_move_was_capture = was_capture
        self.last_move = (src, dst)