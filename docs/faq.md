# FAQ

This FAQ answers common questions about the Baten Chess Engine.

### Q1: What is the `C*10 + R` square encoding?

**A:** Each board square is encoded as an integer where:

* **C** = column (1 for 'a', 2 for 'b', … 8 for 'h')
* **R** = row (1 at White's back rank, up to 8 at Black's back rank)

For example:

* `a1` → `1*10 + 1 = 11`
* `e2` → `5*10 + 2 = 52`
* `h8` → `8*10 + 8 = 88`

This simple arithmetic avoids matrices or bitboards.

---

### Q2: How do I add a new piece or variant?

**A:** Use the DSL YAML specs in `dsl/`:

1. Create a new `spec_<piece>.yaml` describing movements.
2. Run `python -m dsl.generate_dsl` to regenerate `validator_dsl.py`.
3. Update `rules.py` if your piece has special rules (e.g., castling-like behavior).
4. Restart the server.

---

### Q3: How does en passant work?

**A:**

* The DSL validator allows diagonal moves when `dst == state.en_passant_target`.
* In the rule engine, if a pawn moves to `en_passant_target`, the captured pawn behind it is removed.
* `en_passant_target` is set in `apply_move` when a pawn does a double-step.

---

### Q4: How is check/checkmate detected?

**A:**

* **Check**: `is_in_check()` searches for any enemy attacking the king's square via pure geometry.
* **Checkmate**: not implemented yet, but can be added by checking if the side in check has any legal moves.

---

### Q5: Can I use this engine without Flask?

**A:** Yes:

```python
from baten_chess_engine.board import Board
from baten_chess_engine.rules import is_move_legal

board = Board()
board.load_fen("...")

if is_move_legal('wP', 52, 53, board, board.last_move):
    board.apply_move('wP', 52, 53)
```

---

### Q6: How do I run tests?

```bash
pytest
```

---

### Q7: Where can I find the license?

See `LICENSE.md` in the project root for the Creative Commons BY-NC 4.0 terms.
