# app.py

from flask import Flask, render_template, request, jsonify

# 1️⃣ Imports pour la marche et les règles
from baten_chess_engine.validator_dsl import is_valid_move_dsl
from baten_chess_engine.rules import (
    is_in_check, square_attacked,
    move_respects_pin, castling_allowed, opposite
)
from baten_chess_engine.board import Board  # Import du Board

# --- 2️⃣ Fonction de validation globale ---
def is_move_legal(piece: str, src: int, dst: int, board: Board, last_move=None) -> bool:
    # 1) marche pure
    if not is_valid_move_dsl(piece, src, dst, board, last_move):
        return False

    # 2) on simule
    new_board = board.copy()
    new_board.apply_move(piece, src, dst)
    new_board.last_move = (src, dst)

    color = piece[0]

    # 3) pas d’échec après coup
    if is_in_check(new_board, color):
        return False

    # 4) cas du roi : pas sur case attaquée + roque
    if piece[1] == 'K':
        if square_attacked(dst, opposite(color), new_board):
            return False
        if abs(src - dst) == 2 and not castling_allowed(src, dst, board):
            return False

    # 5) clouages
    if not move_respects_pin(piece, src, dst, board):
        return False

    return True

# --- 3️⃣ Création de l’app et du plateau initial ---
app = Flask(__name__)
board = Board()
board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

# --- 4️⃣ Route racine pour afficher le damier ---
@app.route("/")
def index():
    return render_template("board.html", pieces=board.pieces)

# --- 5️⃣ Route de validation ---
@app.route("/validate", methods=["POST"])
def validate():
    data = request.get_json()
    piece = data["piece"]
    src   = data["src"]
    dst   = data["dst"]

    last_move = getattr(board, "last_move", None)

    # on appelle la validation globale
    valid = is_move_legal(piece, src, dst, board, last_move)

    # si OK, on applique le coup pour mettre à jour le plateau
    if valid:
        board.apply_move(piece, src, dst)
        board.last_move = (src, dst)

    return jsonify({"valid": valid, "pieces": board.pieces})

if __name__ == "__main__":
    app.run(debug=True)
