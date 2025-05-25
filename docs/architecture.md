# Architecture

This document describes the overall architecture of the Baten Chess Engine, from the front-end UI down to the board state and validator.

## High-Level Overview

[ Web UI (Flask + HTML/CSS/JS) ]
↓
[ REST API / app.py ]
• routes: / (board), /validate, /reset
↓
[ Rule Engine (rules.py) ]
• turn management
• destination occupation
• pure movement dispatch → validator_dsl
• simulation + check + special rules (castling, en-passant, promotion)
• pins, check detection
↓
[ Movement Validator (validator_dsl.py) ]
• pure kinematics for each piece type
• geometry (rook, bishop, knight, queen, pawn, king)
• sliding obstruction (path_clear)
↓
[ Board Model (board.py) ]
• pieces: Dict[int,str]
• load_fen(), apply_move(), castling rights, en-passant target, history
• path_clear(), is_empty(), is_enemy()

## Components

### 1. Front-End UI (`templates/board.html` + `static/`)
- Interactive chessboard rendered by Flask/Jinja2.  
- Drag-&-drop events trigger POST `/validate`.  
- Renders Unicode piece glyphs and highlights legal/illegal moves.

### 2. REST API (`app.py`)
- `GET /` → serve the board UI.  
- `POST /validate` → calls `is_move_legal()`, returns `{ valid, pieces }`.  
- `POST /reset` → resets board to initial FEN.  
- Manages `board.turn`, `board.last_move`, and logs each step.

### 3. Rule Engine (`rules.py`)
- **`is_move_legal()`** orchestrates full legality:  
  1. Turn check  
  2. Destination occupation  
  3. Pure movement (dispatch to DSL)  
  4. Simulation + self-check prevention  
  5. King special (castling, attacked squares)  
  6. En-passant capture  
  7. Promotions (state update)  
  8. Pin detection  
- **`is_in_check()`**, **`square_attacked()`**, **`castling_allowed()`**, **`move_respects_pin()`**.

### 4. Movement Validator (DSL) (`validator_dsl.py`)
- Auto-generated from YAML specs in `dsl/`.  
- Implements **pure geometry**:  
  - Rook: same row/column + no obstruction  
  - Bishop: diagonal + no obstruction  
  - Queen: rook ∪ bishop  
  - Knight: L-shape  
  - Pawn: advances & captures (flags en-passant)  
  - King: one-step moves  
- Completely **stateless** regarding turn, captures, or special rules.

### 5. Board Model (`board.py`)
- Maintains `pieces` map: square code → piece code (`'wP'`, `'bK'`, …).  
- FEN loading/parsing.  
- `path_clear(src, dst)` for sliding pieces.  
- Castling rights, en-passant target, game history (for threefold repetition).

## Data Flow

1. **User** drags a piece → browser computes `piece`, `src`, `dst`.  
2. **UI JS** sends JSON to `/validate`.  
3. **`app.py`** invokes `is_move_legal()`.  
4. **`rules.py`** calls into **`validator_dsl.py`** for pure movement.  
5. **`rules.py`** simulates move, checks special rules and check/pin.  
6. **`app.py`** updates `Board` if legal; returns new `pieces` map to UI.  
7. **UI** re-renders the board.

## Extensibility

- **Variants**: swap in a different `rules_xyz.py` or override `is_move_legal`.  
- **New pieces**: add YAML spec in `dsl/`, re-generate `validator_dsl.py`, and extend `rules.py` if needed.  
- **Language ports**: the lightweight core (pure geometry + simple state) can be ported to Rust or C++ for performance.

---

With this reference, contributors and end-users can quickly grasp how each module interacts and where to extend or debug.
