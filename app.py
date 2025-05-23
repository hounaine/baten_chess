# app.py

from flask import Flask, render_template, request, jsonify
from baten_chess_engine.board import Board
from baten_chess_engine.validator_dsl import is_valid_move_dsl as is_valid_move

app = Flask(__name__)
board = Board()
board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

@app.route("/")
def index():
    return render_template("board.html", pieces=board.pieces)

@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    src, dst = data["src"], data["dst"]
    print("Attempting move:", data["piece"], "from", src, "to", dst)
    print("Before:", board.pieces)
    valid = is_valid_move(data["piece"], src, dst, board, board.last_move)
    if valid:
        board.apply_move(data["piece"], src, dst)
        print("After :", board.pieces)
    return jsonify({"valid": valid, "turn": board.turn})


if __name__ == "__main__":
    app.run(debug=True)
