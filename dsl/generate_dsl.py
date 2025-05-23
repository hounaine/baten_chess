import yaml
from dsl.chess_dsl import State, generate_code
import glob
import os

def load_spec(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def process_spec(path):
    spec = load_spec(path)
    name = os.path.splitext(os.path.basename(path))[0]  # 'spec_knight'
    piece_type = spec['transitions'][0]['piece_type']
    Jeu = State('Jeu', spec['fields'])

    @Jeu.transition(f"Move{piece_type}")
    def move_piece(state, piece, src, dst):
        pass

    code = generate_code(Jeu)
    out = f"baten_chess_engine/validator_dsl.py"
    with open(out, 'a') as f:  # append to the same file
        f.write("\n\n" + code)

if __name__ == '__main__':
    # Génère d'abord le code pour la tour, puis pour le cavalier
    for spec_file in ['dsl/spec_rook.yaml', 'dsl/spec_knight.yaml']:
        process_spec(spec_file)
