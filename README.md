# Baten Chess Engine

Lightweight, extensible chess engine prototype implemented in Python with a Flask interface.  
Validates all legal moves (castling, en passant, promotion, check/checkmate) via a state-machine and a mini-DSL.

---

## Installation

```bash
git clone https://github.com/hounaine/baten_chess.git
cd baten_chess
python3 -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
