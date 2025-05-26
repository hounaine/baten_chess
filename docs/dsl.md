# DSL & Generation

This document explains how to use the mini-DSL to declaratively define piece movements and auto-generate the validator code.

## Overview

The DSL is based on **YAML specifications** stored under the `dsl/` directory. Each file (e.g., `spec_rook.yaml`) defines:

* **piece\_type**: e.g., `R` for rook.
* **fields**: any state fields needed (e.g., `en_passant_target`).
* **transitions**: list of movement rules, with conditions and updates.

A Python script `dsl/generate_dsl.py` reads these specs and writes `validator_dsl.py`.

## Spec Structure

```yaml
# spec_rook.yaml
piece_type: R
fields:
  - pieces
  - castling_rights
  - en_passant_target
transitions:
  - name: MoveR
    description: "Rook moves horizontally or vertically, any distance"
    condition:
      type: geometry
      directions:
        - horizontal
        - vertical
    updates:
      - none
```

* `piece_type`: one-letter code.
* `fields`: state attributes used.
* `transitions`: each defines a rule:

  * `name`: internal transition name.
  * `description`: human-readable.
  * `condition`: can be `geometry` with directions, or `difference_set`.
  * `updates`: how to update state (e.g., set `en_passant_target`).

## Generating the Validator

Run:

```bash
python -m dsl.generate_dsl
```

This will:

1. Parse all `dsl/spec_*.yaml` files.
2. For each, instantiate a `State` and register transitions.
3. Append generated Python code into `baten_chess_engine/validator_dsl.py`.

Inspect the top of `validator_dsl.py` to see the auto-generated functions: `is_valid_rook_move`, etc.

## Adding a New Piece or Move

1. **Create** a new spec file in `dsl/`, e.g., `spec_archbishop.yaml`.
2. **Define** `piece_type: A`, appropriate `transitions` (e.g., combining bishop+knight deltas).
3. Run `python -m dsl.generate_dsl`.
4. **Import** and integrate in `rules.py` if special rules apply.

## Advanced: Custom Conditions

The DSL supports different condition types:

* `geometry`: horizontal, vertical, diagonal.
* `difference_set`: list of allowed numeric diffs.
* `knight`: L-shape deltas.
* `pawn`: includes `initial_double`, `diagonal_capture`.

Example for knight:

```yaml
piece_type: N
fields: []
transitions:
  - name: MoveN
    condition:
      type: knight
```

This generates `is_valid_knight_move` automatically.
