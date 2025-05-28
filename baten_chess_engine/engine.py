# baten_chess_engine/engine.py

import sys
from .board import Board
from .validator_dsl import is_valid_move

def main():
    board = Board()
    print("Baten Chess Engine (mode CLI simplifié)")
    print("Entrez des commandes UCI basiques (uci, position, go, quit).")
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        cmd = line.strip().split()
        if cmd[0] == "uci":
            print("id name BatenChessEngine")
            print("id author VotreNom")
            print("uciok")
        elif cmd[0] == "position":
            # Exemple minimal : position startpos moves e2e4 …
            # À enrichir pour gérer fen et moves
            print("position ignored (prototype)")
        elif cmd[0] == "go":
            # Prototype renvoyant un coup factice
            print("bestmove 0000")
        elif cmd[0] == "quit":
            break

if __name__ == "__main__":
    main()
