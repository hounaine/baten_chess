# fichier : baten_chess_engine/__init__.py

# on ré-exporte dans l'espace de noms root ce qui est désormais dans core
from .core.board        import Board
from .core.move_validator import is_valid_move
from .core.check_rules  import is_checkmate, is_stalemate, generate_legal_moves
from .core.rules        import *   # ou, mieux, listez explicitement vos fonctions/règles

class ChessEngine:
	def __init__(self):
		self.last_move_was_capture: bool = False
