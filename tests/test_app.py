import json
import pytest
from chess_app import app, board, engine
from baten_chess_engine.board import Board

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        # Réinitialiser l’état avant chaque test
        board.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
        board.turn = 'w'
        board.last_move = None
        board.game_over = False
        engine.current_phase = engine.phases[0]
        yield c

def post_move(client, piece, src, dst):
    return client.post(
        "/validate",
        data=json.dumps({"piece": piece, "src": src, "dst": dst}),
        content_type='application/json'
    )

def test_valid_move_switch_turn(client):
    # 1. e2→e4 (82→84)
    rv = post_move(client, 'wP', 82, 84)
    data = rv.get_json()
    assert data['valid']
    assert data['turn'] == 'b'
    assert 'message' not in data

def test_illegal_move_wrong_turn(client):
    # Essayer un coup noir alors que c'est blanc
    rv = post_move(client, 'bP', 87, 85)
    data = rv.get_json()
    assert not data['valid']
    assert data['turn'] == 'w'
    assert "wrong_turn" not in data['message']  # ou votre message localisé

def test_illegal_move_self_check(client):
    # Placer un scénario échec et tenter un coup qui laisse en échec
    # Roi blanc e1 (51), tour noire e8 (58)
    board.pieces = {51:'wK', 58:'bR'}
    board.turn = 'w'
    rv = post_move(client, 'wK', 51, 52)  # roi tente f1, attaqué
    data = rv.get_json()
    assert not data['valid']
    assert "in_check" in data['message']

def test_checkmate_message_and_game_over(client):
    # Mat simple : roi noir a8 (18), dame blanche b7 (27), roi blanc c6 (36)
    board.pieces = {18:'bK',27:'wQ',36:'wK'}
    board.turn = 'b'
    board.last_move = None
    rv = post_move(client, 'bK', 18, 19)  # n’importe quel coup illégal
    data = rv.get_json()
    # Après une tentative, game_over doit être True
    assert board.game_over
    assert not data['valid']
    assert "checkmate" in data['message']

def test_reset(client):
    # Jouer un coup, puis reset
    post_move(client, 'wP', 82, 84)
    rv = client.get("/reset")
    data = rv.get_json()
    assert data['status'] == 'success'
    # Le tour est revenu à 'w' et position initiale
    assert board.turn == 'w'
    assert board.pieces[81] == 'wR'  # tour en a1

