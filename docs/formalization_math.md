# Mathematical Formalization of Move Validation

This document presents a concise formal model of the mechanics and rules underpinning the Baten Chess Engine. It is designed to be both general (supporting arbitrary board sizes and fairy‐chess variants) and precise, separating geometric “kinematics” from game “guard” rules.

---

## 1. Board and Coordinates

Let:

- \(W, H \in \mathbb{N}\) be the board width (number of columns) and height (number of rows).  
- \(B = \{(c,r) \mid 1 \le c \le W,\; 1 \le r \le H\}\) the set of all squares.

We define a coding function for convenience:

\[
\mathrm{code}(c,r) = 10 \times c + r,
\]

mapping each square to a unique integer in \(\{11,12,\dots,W\times10 + H\}\).  
Alternatively, we may also work directly with coordinates \((c,r)\).

We view the board as a graph \(G=(B,E)\), where

\[
E = \{\,((c,r),(c',r')) \mid (c',r') - (c,r) \in \Delta\}
\]

for some set of elementary offsets \(\Delta\).

---

## 2. Elementary Moves and Delta Sets

For each piece type \(p \in \{P,N,B,R,Q,K\}\), define a set of elementary displacement vectors

\[
\Delta_p \subset \mathbb{Z}^2
\]

representing one “step” of that piece.

- **Pawn (white)**:  
  - Forward: \(\Delta_{P,w}^{\text{adv}} = \{(0,+1)\}\)  
  - Double-step: two steps \((0,+2)\) from rank 2 (handled separately).  
  - Capture: \(\Delta_{P,w}^{\text{cap}} = \{(+1,+1),(-1,+1)\}\).  

- **Pawn (black)**:  
  - Forward: \(\Delta_{P,b}^{\text{adv}} = \{(0,-1)\}\)  
  - Double-step: \((0,-2)\) from rank 7.  
  - Capture: \(\Delta_{P,b}^{\text{cap}} = \{(+1,-1),(-1,-1)\}\).  

- **Knight**:  
  \[
    \Delta_N = \{(\pm1,\pm2),(\pm2,\pm1)\}.
  \]

- **Bishop**:  
  \[
    \Delta_B = \{(\pm1,\pm1)\}.
  \]

- **Rook**:  
  \[
    \Delta_R = \{(\pm1,0),(0,\pm1)\}.
  \]

- **Queen**:  
  \(\Delta_Q = \Delta_R \cup \Delta_B.\)

- **King**:  
  \(\Delta_K = \Delta_Q.\)

---

## 3. Legal Moves and Path Clearance

### 3.1 Non‐sliding pieces (Knight, King, Pawn captures)

A move from \(u=(c,r)\) to \(v=(c',r')\) is kinematically valid if

\[
v - u \in \Delta_p
\]

(or \(2\cdot(0,\pm1)\) for pawn double‐step), and the target square is empty or occupied by an enemy piece.

### 3.2 Sliding pieces (Bishop, Rook, Queen)

A move \(u \to v\) is valid iff there exists a direction \(d\in\Delta_p\) and an integer \(k\ge1\) such that

\[
v = u + k\,d,
\]

and all intermediate squares:

\[
u + d,\;u + 2d,\;\dots,\;u + (k-1)d
\]

are empty. We implement this via a `path_clear(src,dst)` predicate that iterates:

```python
step = encode(d)  # e.g. (1,0)->+10, (0,1)->+1, or diagonal
pos = src + step
while pos != dst:
    if pos in pieces: return False
    pos += step
return True
