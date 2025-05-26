# Test Plan for Baten Chess Engine

This document outlines the tests and scenarios to validate the correctness of the engine.

## 1. Unit Tests

### a. Movement Validator (`validator_dsl.py`)

* **Rook**:

  * Move horizontally across empty path (e.g., a1→a4). Should be valid.
  * Move vertically across empty path (e.g., a1→d1). Should be valid.
  * Attempt diagonal move (e.g., a1→b2). Should be invalid.
  * Attempt blocked move (e.g., a1→a8 with pawn on a4). Should be invalid.

* **Bishop**:

  * Diagonal moves with clear path. Valid.
  * Straight moves. Invalid.
  * Blocked diagonal. Invalid.

* **Queen**:

  * Combines rook + bishop. Test both axes and diagonal.

* **Knight**:

  * L-shaped moves. Valid.
  * Non-L moves. Invalid.

* **Pawn**:

  * Single advance, double advance from initial rank.
  * Diagonal capture including en-passant.
  * Invalid lateral moves.

* **King**:

  * One-step in all directions. Valid.
  * Two-step castle move (geometry valid, rule engine may reject based on rights). Valid geometry.

### b. Rule Engine (`rules.py`)

* **Turn enforcement**: cannot move opponent's piece.
* **Self-check prevention**: moving pinned piece invalidates.
* **Castling**:

  * King-side and queen-side under various scenarios (rights, clear path, attacked squares).
* **En-passant**:

  * Valid only immediately after double-step.
* **Promotion**:

  * Pawn reaching last rank flagged for promotion update.

## 2. Integration Tests (Flask)

* **`/validate` endpoint**

  * Valid move returns `200` with `valid: true` and updated pieces map.
  * Invalid move returns `200` with `valid: false`.
  * Malformed JSON returns `400`.

* **`/reset` endpoint**

  * Resets board and returns `status: success`.

## 3. End-to-End (Browser UI)

* Launch UI and perform moves via drag & drop.
* Verify correct piece placement after valid moves.
* Verify rejection visual feedback on invalid moves.
* Test reset button (if implemented).

## Running Tests

```bash
pytest --maxfail=1 --disable-warnings -q
```

