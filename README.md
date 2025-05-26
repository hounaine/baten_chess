# Baten Chess Engine

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]() [![Version](https://img.shields.io/badge/version-v0.2-blue)]() [![License](https://img.shields.io/badge/license-CC--BY_NC--4.0-lightgrey)]()

**Baten Chess Engine** is a lightweight, mathematically elegant chess engine built in Python, with a modular architecture designed for extensibility, formal proofs, and easy porting to Rust or C++.
It treats **any board game** as a variant: you can define square or rectangular boards of any size, craft custom fairy pieces, and specify rules declaratively via a mini-DSL.
Use the same core to build classic chess, exotic fairy variants, or entirely new board games.

## Key Features

### Core Engine

* **Difference-Based Validation**: generic move validation via `|src - dst| ∈ Sₚ`, inspired by Fibochess Theory.
* **Extensible Architecture**: add new games or variants without altering the core logic.

### Variant Support

* **Universal Board Support**: works on any rectangular grid, not just 8×8.
* **Mini-DSL**: define and generate piece movements in YAML, including custom fairy pieces.
* **Dynamic Rule Engine**: plug in new rules for castling, en-passant, promotions, or bespoke mechanics.

### UI & Integration

* **Interactive Web UI**: Flask server with drag-and-drop UI that adapts to custom board sizes.
* **FEN & Variants**: load/save standard FEN or custom notations for variant positions.

## Getting Started

Clone the repo, install dependencies, and run the server:

```bash
# Clone & enter
git clone https://github.com/hounaine/baten_chess.git
cd baten_chess

# Setup
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run
flask run  # or python app.py
```

Open your browser at `http://127.0.0.1:5000` to see the interactive board.

## Documentation

Browse full docs in `docs/`:

* [Install](docs/install.md)
* [Usage](docs/usage.md)
* [Architecture](docs/architecture.md)
* [DSL & Generation](docs/dsl.md)
* [Rule Engine](docs/rules.md)
* [Board API](docs/board_api.md)
* [REST API](docs/app_api.md)
* [Contributing](docs/contributing.md)
* [FAQ](docs/faq.md)
* [Changelog](docs/changelog.md)

---

*Build your own fairy chess variants with ease!*
