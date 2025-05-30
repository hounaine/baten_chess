# Rule Engine Reference

This document details the rule-engine (`rules.py`) that enforces all game rules beyond pure movement.

## Overview

`rules.py` contains:

* `opposite(color)` : switch turn between 'w' and 'b'.
* `square_attacked(cell, attacker_color, board)` : check if a cell is attacked by any piece of a given color.
* `is_in_check(board, color)` : determine if `color`'s king is in check.
* `castling_allowed(src, dst, board)` : validate castling move.
* `move_respects_pin(piece, src, dst, board)` : ensure a pinned piece doesn't expose king.
* `is_move_legal(piece, src, dst, board, last_move)` : main entry point combining all rules.

## 1. Turn Management

```python
def opposite(color: str) -> str:
    """Return the opposite color: 'w' -> 'b', 'b' -> 'w'."""
    return 'b' if color == 'w' else 'w'
```

* Called after a legal move to switch `board.turn`.
* Used to verify correct player move.

## 2. Occupation Check

Within `is_move_legal`:

```python
# destination must be empty or enemy (except en-passant)
if dst in board.pieces and board.pieces[dst][0] == color:
    return False
```

Ensures you cannot move onto a friendly piece.

## 3. Pure Movement Dispatch

`is_move_legal` calls into DSL validators:

```python
from batter_chess_engine.validator_dsl import is_valid_move
if not is_valid_move(piece, src, dst, board, last_move):
    return False
```

This enforces geometry (rook, knight, etc.) and obstruction.

## 4. Self-Check Prevention

Simulate the move and verify king safety:

```python
new = copy.deepcopy(board)
# apply move in new
if is_in_check(new, color):
    return False
```

Prevents any move that leaves own king in check.

## 5. King-Specific Rules

* **Castling**: `castling_allowed(src, dst, board)`. Checks:

  * Castling rights flag (K/Q/k/q)
  * Path between king and rook clear
  * King not in, through, or into check

* **No moving into attacked square**: handled via `square_attacked` during castling simulation.

## 6. En Passant

Within `is_move_legal` for pawns:

```python
if piece[1]=='P' and dst == board.en_passant_target:
    # remove captured pawn behind
```

Handles the special diagonal capture.

## 7. Pin Handling

```python
def move_respects_pin(...):
    # simulate moving piece
    # check if own king is in check
    # revert simulation
    return not pinned
```

Ensures pinned pieces cannot move illegally.

## 8. Promotion (State Update)

Promotion affects `board.pieces[dst]` and piece type.
Not handled in `is_move_legal` but during state update after validation.

## 9. FEN Repetition & Draws

`board.history` stores snapshots for threefold repetition.
Checks for draw conditions are outside this engine (future work).
