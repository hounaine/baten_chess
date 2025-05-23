
---
<!-- test change -->

### `docs/index.md`

```markdown
# Baten Chess Engine Documentation

## À propos / About

**FR :**  
Baten Chess Engine est un moteur d’échecs original et léger, conçu pour allier performance et élégance mathématique.  
- **Objectif** : formaliser la validation des coups grâce au calcul de |src − dst| ∈ S<sub>p</sub>, où chaque pièce dispose de son propre ensemble de différences, inspiré de la Fibochess Theory.  
- **Fonctionnalités** :  
  - Chargement de position FEN,  
  - Validation de tous les coups légaux (prise en passant, roque, promotion, échec/échec-et-mat, répétition),  
  - Application des coups sur un plateau Web interactif (Flask + drag & drop),  
  - Mini-DSL (YAML + Python) pour décrire et générer automatiquement la logique de validation.  
- **Originalité** :  
  - Remplacement des bitboards par une simple relation de différences,  
  - Automate d’états mathématiquement rigoureux,  
  - Séparation stricte validation vs mise à jour d’état,  
  - Architecture facilement extensible et maintenable.

**EN :**
Baten Chess Engine is a lightweight, extensible chess engine designed to combine performance with mathematical elegance.  
- **Goal**: formalize move validation using |src − dst| ∈ S<sub>p</sub>, where each piece has its own set of allowed differences, inspired by the Fibochess Theory.  
- **Features**:  
  - FEN position loading,  
  - Full legal move validation (en passant, castling, promotion, check/checkmate, repetition),  
  - Interactive web board (Flask + drag & drop),  
  - Mini-DSL (YAML + Python) for declaratively describing and auto-generating validation logic.  
- **Originality**:  
  - Replaces traditional bitboards with a simple difference-based relation,  
  - State-machine architecture with a formal mathematical model,  
  - Clear separation of validation vs state update,  
  - Highly extensible and maintainable design.

  ## Avantages / Benefits

**FR :**  
- **Simplicité** : validation par la différence des codes de cases (src et dst sont les indices de cases codés par colonne×10 + rangée), |src – dst| ∈ Sₚ.  
- **Extensible** : ajoutez ou modifiez des règles via la mini-DSL YAML/Python.  
- **Performant** : cœur Python léger, prêt à porter en Rust ou C++.  
- **Interactif** : interface Web Flask avec glisser-déposer des pièces.  
- **Rigoureux** : architecture en automate d’états formel, facilement vérifiable.

**EN :**  
- **Simplicity**: move validation by the difference between square codes (src and dst are the square indices encoded as column×10 + row), |src – dst| ∈ Sₚ.  
- **Extensible**: easily add or modify rules via the YAML/Python mini-DSL.  
- **Efficient**: lightweight Python core, ready for a Rust or C++ port.  
- **Interactive**: Flask web UI with drag-and-drop.  
- **Rigorous**: formal state-machine architecture, easy to verify.

## Principe de validation / Validation Principle

**FR :**  
Chaque case du plateau est codée par un entier `C*10 + L` (C = colonne 1→8, L = rangée 1→8), par ex.  
- `a1` = 11,  
- `e2` = 52,  
- `h8` = 88.  

Pour toute pièce, on note **src** (source) et **dst** (destination) ces codes de cases.  
Un coup est valide si la valeur absolue de la différence entre le code de la case source (src) et celui de la case destination (dst) appartient à l’ensemble Sₚ.  

- **Pion** :  
  - Avancée : **Sₚ** = {1, 2} (1 ou 2 rangées vers l’avant)  
  - Prise : **Sₚ** = {9, 11} (diagonales)  
  - *Ex.* :  
    - e2 → e3 : **src** = 52, **dst** = 53 → |52−53| = 1 (valide)  
    - e4 → f5 : **src** = 54, **dst** = 65 → |54−65| = 11 (valide)  

- **Tour** :  
  - **Sₚ** = {1, 2, …, 7} ∪ {10, 20, …, 70}  
  - *Ex.* :  
    - a1 → a4 : **src** = 11, **dst** = 14 → |11−14| = 3 (valide)  
    - d5 → g5 : **src** = 45, **dst** = 75 → |45−75| = 30 (valide)  

**EN :**  
Each square is encoded as the integer `C*10 + L` (C = column 1→8, L = row 1→8), e.g.  
- `a1` = 11,  
- `e2` = 52,  
- `h8` = 88.  

We call these codes **src** (source) and **dst** (destination).  
A move is valid if the absolute value of the difference between the source square code (src) and the destination square code (dst) lies in the set Sₚ.  

- **Pawn**:  
  - Forward: **Sₚ** = {1, 2} (one or two ranks)  
  - Capture: **Sₚ** = {9, 11} (diagonals)  
  - *E.g.*:  
    - e2 → e3: **src** = 52, **dst** = 53 → |52−53| = 1 (valid)  
    - e4 → f5: **src** = 54, **dst** = 65 → |54−65| = 11 (valid)  

- **Rook**:  
  - **Sₚ** = {1, 2, …, 7} ∪ {10, 20, …, 70}  
  - *E.g.*:  
    - a1 → a4: **src** = 11, **dst** = 14 → |11−14| = 3 (valid)  
    - d5 → g5: **src** = 45, **dst** = 75 → |45−75| = 30 (valid)  

## Contents

- [Installation](install.md)  
- [Usage](usage.md)  
- [Architecture](architecture.md)  
- [DSL & Generation](dsl.md)  
- [API Reference](api_reference.md)  
- [Tests](tests.md)  
- [FAQ](faq.md)

---

To get started, see the **README.md** at the project root.