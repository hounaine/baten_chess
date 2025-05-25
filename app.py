# app.py

from flask import Flask, render_template, request, jsonify
import logging
import copy
from baten_chess_engine.rules import opposite

# Configure logging
logging.basicConfig(level=logging.INFO)

from baten_chess_engine.validator_dsl import is_valid_move_dsl
from baten_chess_engine.rules import (
    is_in_check, square_attacked,
    move_respects_pin, castling_allowed, opposite
)
from baten_chess_engine.board import Board

def is_move_legal(piece: str, src: int, dst: int, board: Board, last_move=None) -> bool:
    # 1) marche pure
    pure_valid = is_valid_move_dsl(piece, src, dst, board, last_move)
    logging.info(f"[app.py] is_move_legal → pure_valid: {pure_valid}")
    if not pure_valid:
        logging.info("[app.py] rejected at pure move validation")
        return False

    # 2) on simule le coup
    new_board = copy.deepcopy(board)
    new_board.apply_move(piece, src, dst)
    new_board.last_move = (src, dst)
    logging.info(f"[app.py] simulated move, new_board.last_move: {new_board.last_move}")

    color = piece[0]

    # 3) pas d’échec après coup
    in_check = is_in_check(new_board, color)
    logging.info(f"[app.py] is_in_check after move: {in_check}")
    if in_check:
        logging.info("[app.py] rejected because king would be in check")
        return False

    # 4) cas du roi : pas sur case attaquée + roque
    if piece[1] == 'K':
        attacked = square_attacked(dst, opposite(color), new_board)
        logging.info(f"[app.py] king moving into attacked square? {attacked}")
        if attacked:
            logging.info("[app.py] rejected because king moving into attacked square")
            return False

        if abs(src - dst) == 2:
            castling_ok = castling_allowed(src, dst, board)
            logging.info(f"[app.py] castling_allowed? {castling_ok}")
            if not castling_ok:
                logging.info("[app.py] rejected castling")
                return False

    # 5) clouages (pin)
    pin_ok = move_respects_pin(piece, src, dst, board)
    logging.info(f"[app.py] move_respects_pin: {pin_ok}")
    if not pin_ok:
        logging.info("[app.py] rejected due to pin")
        return False

    logging.info("[app.py] move_legal → True")
    return True

# --- Création de l’app et du plateau initial ---
app = Flask(__name__)
board = Board()
board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
board.turn = 'w'
board.last_move = None

@app.route("/")
def index():
    return render_template("board.html", pieces=board.pieces)

@app.route("/validate", methods=["POST"])
def validate():
    try:
        data = request.get_json()
        piece = data.get("piece")
        src   = data.get("src")
        dst   = data.get("dst")
        if not piece or src is None or dst is None:
            return jsonify({"error": "Invalid input"}), 400

        # Hors-tour → refus simple
        if piece[0] != board.turn:
            logging.info(f"[app.py] Rejected: not {board.turn}'s turn")
            return jsonify({"valid": False}), 200

        logging.info(f"[app.py] Attempting move: {piece!r} from {src} to {dst}")
        logging.info(f"[app.py] board.turn = {board.turn!r}, last_move = {board.last_move!r}")

        valid = is_move_legal(piece, src, dst, board, board.last_move)
        logging.info(f"[app.py] → is_move_legal: {valid}")

        if valid:
            board.apply_move(piece, src, dst)
            board.last_move = (src, dst)
            board.turn = opposite(board.turn)
            logging.info(f"[app.py] Move applied. Next turn: {board.turn!r}")
        else:
            logging.info("[app.py] Move rejected")

        return jsonify({"valid": valid, "pieces": board.pieces})
    except Exception as e:
        logging.error(f"[app.py] Error during move validation: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/reset", methods=["GET", "POST"])
def reset_board():
    try:
        board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        board.turn = 'w'
        board.last_move = None
        logging.info("[app.py] Board reset to initial state.")
        return jsonify({"status": "success", "pieces": board.pieces})
    except Exception as e:
        logging.error(f"[app.py] Error during board reset: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
