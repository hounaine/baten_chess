# chess_app.py

from flask import Flask, render_template, request, jsonify
import logging
import copy

from alternation_engine import (
    AlternationEngine, Phase,
    NeverAlternate, StrictAlternate,
    MoveContext
)

from baten_chess_engine import error_messages
from baten_chess_engine.core.rules import generate_legal_moves

# Règles de base

# Génération de coups & fin de partie

from baten_chess_engine import (
    Board,
    is_valid_move,
    is_in_check, square_attacked, move_respects_pin, castling_allowed, opposite,
    generate_legal_moves, is_checkmate, is_stalemate,
    error_messages
 )

def is_checkmate(board, color):
    """
    Retourne True si le roi de la couleur donnée est en échec et n'a aucun coup légal.
    """
    if not is_in_check(board, color):
        return False
    legal_moves = generate_legal_moves(board, color)
    return len(legal_moves) == 0

# Instantiate error messages
errors = error_messages.ERROR_MESSAGES

# Phases setup for classical chess: strict alternate every move
phases = [
    Phase('battle', StrictAlternate(), lambda ctx: False),
]
engine = AlternationEngine(phases, initial_turn='w')

logging.basicConfig(level=logging.INFO)
app = Flask(__name__,
    template_folder="baten_chess_engine/web/templates",
    static_folder="baten_chess_engine/web/static")

board = Board()
board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

# Helper to list all cells on board
ALL_CELLS = [file * 10 + rank for file in range(1,9) for rank in range(1,9)]

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

        # JSON mal formé ?
        if not piece or src is None or dst is None:
            return jsonify({"valid": False, "message": "invalid_input"}), 400

        # Si la partie est déjà finie
        if getattr(board, "game_over", False):
            return jsonify({
                "valid": False,
                "message": "checkmate",
                "game_over": True
            }), 200

        # Mauvais tour ?
        if piece[0] != board.turn:
            return jsonify({
                "valid": False,
                "message": f"Not {board.turn}'s turn",
                "turn": board.turn,
                "game_over": getattr(board, "game_over", False)
            }), 200

        # Si la position est déjà mat, on termine la partie immédiatement
        if is_checkmate(board, board.turn):
            board.game_over = True
            return jsonify({
                "valid":      False,
                "message":    f"checkmate {board.turn}",
                "game_over":  True
            }), 200

        # 1) Cinématique de base + obstacle
        if not is_valid_move(piece, src, dst, board, board.last_move) or not board.path_clear(src, dst):
            if is_checkmate(board, board.turn):
                board.game_over = True
                return jsonify({
                    "valid": False,
                    "message": "checkmate",
                    "game_over": True
                }), 200
            return jsonify({"valid": False, "message": "invalid_move"}), 200

        # 2) Auto-échec : on simule le coup (pour tout le monde, y compris le roi)
        test_board = copy.deepcopy(board)
        test_board.apply_move(piece, src, dst)
        if is_in_check(test_board, piece[0]):
            if is_checkmate(board, board.turn):
                board.game_over = True
                return jsonify({
                    "valid": False,
                    "message": "checkmate",
                    "game_over": True
                }), 200
            return jsonify({"valid": False, "message": "in_check"}), 200

        # 3) Clouage (jamais pour le roi)
        if piece[1] != 'K' and not move_respects_pin(piece, src, dst, board):
            if is_checkmate(board, board.turn):
                board.game_over = True
                return jsonify({
                    "valid": False,
                    "message": "checkmate",
                    "game_over": True
                }), 200
            return jsonify({"valid": False, "message": "pinned_piece"}), 200

        # 4) Roque
        if piece[1] == 'K' and abs(src - dst) == 20:
            if not castling_allowed(src, dst, board):
                return jsonify({"valid": False, "message": "cannot_castle"}), 200

        # --- à partir d'ici : coup légal, on l'applique ---
        board.apply_move(piece, src, dst)
        board.turn = opposite(board.turn)

        # Prépare la notation et les flags
        flag_check = is_in_check(board, board.turn)
        legal_moves = generate_legal_moves(board, board.turn)
        flag_mate = flag_check and not legal_moves
        if flag_mate:
            board.game_over = True
            suffix = "#"
            message = f"checkmate {board.turn}"
        elif flag_check:
            suffix = "+"
            message = f"check {board.turn}"
        else:
            suffix = ""
            message = None

        move_notation = f"{piece[1]}{src}-{dst}{suffix}"

        resp = {
            "valid":        True,
            "notation":     move_notation,
            "is_check":     flag_check,
            "is_checkmate": flag_mate,
            "pieces":       board.pieces,
            "turn":         board.turn,
            "game_over":    getattr(board, "game_over", False),
        }
        if message:
            resp["message"] = message
        return jsonify(resp), 200

    except Exception as e:
        logging.exception("Erreur dans /validate")
        return jsonify({"valid": False, "message": "internal_error"}), 500

@app.route("/reset", methods=["GET","POST"])
def reset_board():
    board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    board.turn = 'w'
    board.last_move = None
    board.last_move_was_capture = False
    board.game_over = False
    logging.info("Board reset to initial state.")
    return jsonify({"status":"success","pieces":board.pieces}), 200

if __name__ == "__main__":
    app.run(debug=True)