# error_messages.py

"""
Defines standard error messages for move validation.
"""
ERROR_MESSAGES = {
    "wrong_turn": "Ce n'est pas le tour des {player}.",
    "invalid_move": "Coup invalide selon les règles de déplacement.",
    "in_check": "Coup interdit : le roi resterait en échec.",
    "cannot_castle": "Vous ne pouvez pas effectuer ce roque.",
    "pinned_piece": "La pièce est clouée et ne peut pas bouger.",
    "check": "Échec au roi {player} !",
    "checkmate": "Échec et mat ! Le joueur {player} perd.",
}