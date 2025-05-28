# Architecture of the Baten Chess Engine

This document provides both a **high-level overview** and a **detailed technical deep-dive** into the modular components of the Baten Chess Engine. It is intended for developers and mathematicians seeking a thorough understanding of the code structure, algorithms, and extension points.

---

## 1. High-Level Overview

**Layers (top ↓ bottom):**

1. **Web UI** (Flask + HTML/CSS/JS)

   * Renders the chessboard.
   * Captures drag-&-drop, sends JSON to the server.
2. **REST API** (`app.py`)

   * Routes: `/` (board), `/validate`, `/reset`.
   * Orchestrates validation, state update, and responses.
3. **Rule Engine** (`rules.py`)

   * **Turn management**
   * **Destination occupancy**
   * **Pure movement dispatch** → `validator_dsl.py`
   * **Simulation + check prevention**, **special rules** (castling, en-passant, promotion)
   * **Pins**, **check detection**
4. **Movement Validator DSL** (`validator_dsl.py`)

   * Stateless kinematics per piece type
   * Geometry: rook, knight, bishop, queen, pawn, king
   * Sliding obstruction (`path_clear`)
5. **Board Model** (`board.py`)

   * `pieces: Dict[int,str]`
   * `load_fen()`, `apply_move()`, castling rights, en-passant target, history
   * `path_clear()`, `is_empty()`, `is_enemy()`

---

## 2. Module Breakdown

### 2.1 Board Model (`board.py`)

```python
@dataclass
class Board:
    pieces: Dict[int, str]
    castling_rights: Dict[str, bool]
    en_passant_target: Optional[int]
    turn: str
    last_move: Optional[Tuple[int,int]]
    last_move_was_capture: bool

    def load_fen(self, fen: str): ...
    def is_empty(self, cell: int) -> bool: ...
    def path_clear(self, src: int, dst: int) -> bool: ...
    def apply_move(self, piece: str, src: int, dst: int): ...
```

* **Encoding**: square = `file*10 + rank`.
* **`path_clear`**: computes directional step and scans intermediate squares in O(D).
* **`apply_move`**: handles piece movement, captures, en passant, promotions, and updates state flags.

### 2.2 Movement Validator DSL (`validator_dsl.py`)

* Implements **pure geometry** for each piece:

  * Rook: straight lines
  * Bishop: diagonals
  * Queen: union of rook and bishop
  * Knight: L-shape
  * Pawn: forward and diagonal captures
  * King: one-step moves
* **Stateless**: does not consider turn, captures, or special rules.

### 2.3 Core Rules (`rules.py`)

* **`is_move_legal()`** orchestrates full validation:

  1. Turn check
  2. Destination occupation
  3. Pure movement (DSL)
  4. Simulation + self-check prevention (`move_respects_pin`)
  5. King special (castling, attacked squares)
  6. En passant
  7. Promotion state update
  8. Pin detection

* **`is_in_check`**, **`square_attacked`** implement check detection.

* **`castling_allowed`** verifies rights and simulates king path.

* **`move_respects_pin`** deep-copies board to ensure no mutation.

### 2.4 Turn Alternation (`alternation_engine.py`)

```python
class TurnRule(ABC):
    def should_switch(self, ctx: MoveContext) -> bool: ...

class Phase:
    def __init__(self, name, rule, transition_condition): ...

class AlternationEngine:
    def __init__(self, phases, initial_turn='w'): ...
    def register_move(self, ctx): ...
    def get_current_turn(self) -> str: ...
```

* **`StrictAlternate`**, **`NeverAlternate`**, **`AlternateOnCapture`**, **`AlternateOnLastSequence`**.
* **Phases**: each phase has its own `TurnRule` and transition trigger.
* **Engine**: advances phase and toggles turn based solely on rules.

### 2.5 Endgame Logic (`check_rules.py`)

```python
def generate_legal_moves(board, player): ...
def is_checkmate(board, player): ...
def is_stalemate(board, player): ...
```

* Filters in five stages: DSL, path clearance, pin, self-check, castling.
* `is_checkmate`: in check + no legal moves.
* `is_stalemate`: not in check + no legal moves.

---

## 3. Technical Deep Dive

### 3.1 `path_clear` Algorithm

```python
def path_clear(self, src, dst):
    df = (dst//10) - (src//10)
    dr = (dst%10) - (src%10)
    step = sign(df)*10 + sign(dr)
    pos = src + step
    while pos != dst:
        if pos in self.pieces: return False
        pos += step
    return True
```

* **Direction vector** reduces multi-dimensional move to linear scan.

### 3.2 Check Detection

```python
def is_in_check(board, color):
    king = ...
    for src,p in board.pieces.items():
        if p[0]==enemy and can_attack(src,king): return True
    return False
```

* Manual enumeration of piece behaviors ensures accuracy and performance.

### 3.3 Castling Simulation

```python
for square in path:
    tmp = deepcopy(board)
    move king to square
    if is_in_check(tmp,color): return False
```

* Guarantees no intermediate square is attacked.

### 3.4 Pin Check

```python
def move_respects_pin(piece,src,dst,board):
    test = deepcopy(board)
    apply test.move(piece,src,dst)
    return not is_in_check(test,piece[0])
```

* Offloads complexity to isolated copy, preserving original state.

### 3.5 Move Generation and Endgame

```python
moves = generate_legal_moves(board,player)
if not moves:
    if is_in_check(board,player): return 'checkmate'
    else: return 'stalemate'
```

* Exhaustive yet performant for 8×8; future optimizations via incremental and cached attack tables.

---

## 4. Extensibility

* **N-dimensional boards**: generalize cell IDs to tuples; adapt `path_clear`.
* **DSL-defined pieces**: YAML specs drive `validator_dsl` generation.
* **Runtime variant config**: user selects board size, piece specs, and alternation rules without redeploy.

---

## 5. Data Flow Diagram

1. UI drag → sends `{ piece, src, dst }`.
2. `app.py` → `is_move_legal` → `rules.py` → `validator_dsl.py`.
3. `apply_move`, `AlternationEngine` updates turn.
4. `check_rules` determines check/mate/pat.
5. Response `{ valid, pieces, turn, message? }` returned.

