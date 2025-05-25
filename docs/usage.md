# Usage

This guide shows you how to launch and interact with the Baten Chess Engine.

## Launch the Web UI

1. Make sure your virtual environment is active and dependencies are installed (see `install.md`).

2. Run the server:

   # Option A: via Flask CLI
   flask run

   # Option B: directly with Python
   python app.py
Open your browser at:

http://127.0.0.1:5000
You will see an interactive chessboard where you can drag & drop pieces.

Move Validation
Drag & drop a piece from its source square to a target square.

Under the hood, the front-end sends a POST to /validate:
POST /validate HTTP/1.1
Content-Type: application/json

{
  "piece": "wP",  // piece code: color + type (e.g. wR, bQ, wK, etc.)
  "src": 52,      // source square code (C*10 + R)
  "dst": 53       // destination square code
}
The server responds:
{
  "valid": true,       // or false
  "pieces": { ... }    // updated positions if move was applied
}
Valid moves are applied immediately on the board; invalid ones are rejected.

Other Endpoints
Reset the game:

curl -X POST http://127.0.0.1:5000/reset
→ Returns { "status": "success", "pieces": {…} } and resets to the standard starting position.

FEN Support
Although not exposed via REST, you can:

from baten_chess_engine.board import Board

board = Board()
board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
to initialize any position programmatically.

Examples
Pawn move: e2 → e4

{ "piece": "wP", "src": 52, "dst": 54 }
Knight move: g1 → f3

{ "piece": "wN", "src": 71, "dst": 63 }
Queen move: d1 → h5


{ "piece": "wQ", "src": 41, "dst": 85 }
For more advanced usage (embedding into your own app, command-line integration), see app_api.md and board_api.md.