# Board API Reference

This document describes the `Board` class and its methods in `baten_chess_engine/board.py`.

## Class `Board`

```python
class Board:
    pieces: Dict[int, str]
    castling_rights: Dict[str, bool]
    en_passant_target: Optional[int]
    history: List[Tuple[frozenset, Tuple[Tuple[str,bool],...], Optional[int]]]
```

Maintains the complete game state:

* `pieces`: mapping from square code (`C*10+R`) to piece code (`'wP'`, `'bK'`, etc.).
* `castling_rights`: flags `'K','Q','k','q'` indicating availability of castling.
* `en_passant_target`: square code where en-passant is possible next move.
* `history`: list of snapshots for threefold repetition.

---

## Initialization & FEN

```python
board = Board()
board.load_fen(fen: str)
```

* `load_fen`: parses a FEN string, sets up `pieces`, `castling_rights`, `en_passant_target`, and clears `history`.

---

## Query Methods

### `is_empty(cell: int) -> bool`

Returns `True` if `cell` is unoccupied.

### `is_friend(cell: int, color: str) -> bool`

Returns `True` if `cell` has a piece of `color`.

### `is_enemy(cell: int, color: str) -> bool`

Returns `True` if `cell` has a piece of the opposite color.

### `path_clear(src: int, dst: int) -> bool`

Checks that all intermediate squares between `src` and `dst` are empty (for sliding pieces). Uses `divmod` decoding of row/col.

---

## State Updates

### `apply_move(piece: str, src: int, dst: int)`

Applies a validated move:

1. Removes `piece` from `src`.
2. Handles captures at `dst` (including en-passant removal).
3. Updates `pieces[dst] = piece`.
4. Updates `castling_rights` and `en_passant_target` as needed.
5. Calls `record_state()` to save history.

### `record_state()`

Stores a snapshot `(frozenset(pieces.items()), tuple(sorted(castling_rights.items())), en_passant_target)` into `history`.

---

## Usage Example

```python
from baten_chess_engine.board import Board

board = Board()
board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

# Check if square 11 (a1) is occupied
print(board.is_empty(11))  # False

# Validate and apply a move via rule engine
from baten_chess_engine.rules import is_move_legal
move = ('wP', 52, 54)
if is_move_legal(*move, board):
    board.apply_move(*move)

# Inspect updated board
print(board.pieces)
```


