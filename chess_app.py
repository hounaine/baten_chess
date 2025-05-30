# app.py

from flask import Flask, render_template, request, jsonify
import logging
import copy

from alternation_engine import (
    AlternationEngine, Phase,
    NeverAlternate, StrictAlternate,
    MoveContext
)

from baten_chess_engine import error_messages
from baten_chess_engine.move_validator import is_valid_move

# Règles de base
from baten_chess_engine.rules import (
    is_in_check,
    square_attacked,
    move_respects_pin,
    castling_allowed,
    opposite
)

# Génération de coups & fin de partie
from baten_chess_engine.check_rules import (
    generate_legal_moves,
    is_checkmate,
    is_stalemate
)

from baten_chess_engine.board import Board


# Instantiate error messages
errors = error_messages.ERROR_MESSAGES

# Phases setup for classical chess: strict alternate every move
phases = [
    Phase('battle', StrictAlternate(), lambda ctx: False),
]
engine = AlternationEngine(phases, initial_turn='w')

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
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
        data  = request.get_json()
        piece = data.get("piece")
        src   = data.get("src")
        dst   = data.get("dst")

        # —————————————————————————————
        # Validation minimale du JSON
        if not piece or src is None or dst is None:
            msg = "invalid_input"
            return jsonify({
                "valid":   False,
                "pieces":  board.pieces,
                "turn":    board.turn,
                "message": msg
            }), 400
        # —————————————————————————————
        
        # 0) Si la partie est déjà terminée
        if board.game_over:
            return jsonify({
                "valid": False,
                "pieces": board.pieces,
                "turn": board.turn,
                "message": "game_over"
            }), 200

        # 0b) Checkmate / stalemate avant tout coup
        if is_checkmate(board, board.turn):
            board.game_over = True
            return jsonify({
                "valid": False,
                "pieces": board.pieces,
                "turn": board.turn,
                "message": "checkmate"
            }), 200
        if is_stalemate(board, board.turn):
            board.game_over = True
            return jsonify({
                "valid": False,
                "pieces": board.pieces,
                "turn": board.turn,
                "message": "stalemate"
            }), 200

        # 1) Mauvais tour
        if piece[0] != board.turn:
            msg = f"Coup interdit : ce n'est pas au tour des {board.turn}."
            logging.info(msg)
            return jsonify({
                "valid": False,
                "pieces": board.pieces,
                "turn": board.turn,
                "message": msg
            }), 200

        # 2) Cinématique pure + obstacle
        if not is_valid_move(piece, src, dst, board, board.last_move) or not board.path_clear(src, dst):
            msg = "invalid_move"
            return jsonify({
                "valid": False,
                "pieces": board.pieces,
                "turn": board.turn,
                "message": msg
            }), 200

        # 3) Sécurité du roi (auto-échec)
        test_board = copy.deepcopy(board)
        test_board.apply_move(piece, src, dst)
        if is_in_check(test_board, piece[0]):
            msg = "in_check"
            return jsonify({
                "valid": False,
                "pieces": board.pieces,
                "turn": board.turn,
                "message": msg
            }), 200

        # 4) Roque spécifique au roi
        if piece[1] == 'K' and abs(src - dst) == 2:
            if not castling_allowed(src, dst, board):
                msg = "cannot_castle"
                return jsonify({
                    "valid": False,
                    "pieces": board.pieces,
                    "turn": board.turn,
                    "message": msg
                }), 200

        # 5) Clouage (pin)
        tmp_board = copy.deepcopy(board)
        if not move_respects_pin(piece, src, dst, tmp_board):
            msg = "pinned_piece"
            return jsonify({
                "valid": False,
                "pieces": board.pieces,
                "turn": board.turn,
                "message": msg
            }), 200

        # Si tout est OK, on applique le coup
        board.apply_move(piece, src, dst)
        ctx = MoveContext(move=(piece, src, dst), is_capture=board.last_move_was_capture)
        engine.register_move(ctx)
        board.turn = engine.get_current_turn()

        # 6) Détection d’échec / mat / pat
        opp = board.turn
        message = None
        if is_in_check(board, opp):
            # premier niveau : simple échec
            message = errors["check"].format(player=opp)
            # vérification du mat
            legal = generate_legal_moves(board, opp)
            if not legal:
                message = errors["checkmate"].format(player=opp)

        # Réponse finale
        response = {
            "valid": True,
            "pieces": board.pieces,
            "turn": board.turn
        }
        if message:
            response["message"] = message

        return jsonify(response), 200

    except Exception as e:
        logging.error(f"Error during move validation: {e}")
        return jsonify({
            "valid": False,
            "pieces": board.pieces,
            "turn": board.turn,
            "message": "internal_error"
        }), 500


@app.route("/reset", methods=["GET","POST"])
def reset_board():
    board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
    board.turn = 'w'
    board.last_move = None
    board.last_move_was_capture = False
    logging.info("Board reset to initial state.")
    return jsonify({"status":"success","pieces":board.pieces}), 200

if __name__ == "__main__":
    app.run(debug=True)