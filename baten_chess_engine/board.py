# Updated baten_chess_engine/board.py with corrected path_clear

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Tuple, FrozenSet

@dataclass
class Board:
    pieces: Dict[int, str] = field(default_factory=dict)
    castling_rights: Dict[str, bool] = field(default_factory=lambda: {
        'K': True, 'Q': True, 'k': True, 'q': True
    })
    en_passant_target: Optional[int] = None
    turn: str = 'w'
    last_move: Optional[Tuple[int, int]] = None
    history: List[Tuple[FrozenSet[Tuple[int,str]], Tuple[Tuple[str,bool],...], Optional[int], str]] = field(default_factory=list)

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

    def is_empty(self, cell: int) -> bool:
        return cell not in self.pieces

    def is_enemy(self, cell: int, color: str) -> bool:
        p = self.pieces.get(cell)
        return bool(p and p[0] != color)

    def path_clear(self, src: int, dst: int) -> bool:
        """
        Vérifie qu'aucune pièce n'obstrue le segment src → dst
        pour les pièces coulissantes (tour, fou, dame).
        """
        src_C, src_L = divmod(src, 10)
        dst_C, dst_L = divmod(dst, 10)
        dc = dst_C - src_C
        dr = dst_L - src_L
        sc = (dc > 0) - (dc < 0)
        sr = (dr > 0) - (dr < 0)

        # Mouvement vertical (même colonne)
        if dc == 0 and dr != 0:
            step = sr
        # Mouvement horizontal (même rangée)
        elif dr == 0 and dc != 0:
            step = sc * 10
        # Mouvement diagonal
        elif abs(dr) == abs(dc):
            step = sc * 10 + sr
        else:
            # Non coulissant, pas d'obstacle à vérifier
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
        if piece[1] == 'P' and dst == prev_enp and self.last_move:
            lm_src, lm_dst = self.last_move
            if lm_dst in self.pieces:
                del self.pieces[lm_dst]
        if dst in self.pieces:
            del self.pieces[dst]
        self.pieces[dst] = piece
        del self.pieces[src]
        self.last_move = (src, dst)
        self.turn = 'b' if self.turn == 'w' else 'w'

print("Patched Board.path_clear: correct horizontal, vertical, diagonal steps")
