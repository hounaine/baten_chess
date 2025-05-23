# dsl/chess_dsl.py

"""
Mini-DSL pour décrire formellement l'état et les transitions
d'un automate d'échecs, et générer du code Python.
"""

from typing import Any

class State:
    def __init__(self, name: str, fields: list[str]):
        self.name = name
        self.fields = fields
        # liste de tuples (transition_name, method_name)
        self.transitions: list[tuple[str, str]] = []

    def transition(self, name: str):
        """
        Décorateur pour déclarer une transition.
        Usage :
            @MyState.transition('Move')
            def move(...): ...
        """
        def decorator(fn):
            self.transitions.append((name, fn.__name__))
            return fn
        return decorator

def generate_code(state: State) -> str:
    """
    Génère le squelette de classe Python à partir de l'état et de ses transitions.
    Chaque champ devient un attribut, chaque transition une méthode à implémenter.
    """
    lines: list[str] = []
    lines.append(f"class {state.name}State:")
    # Champs de l'état
    for field in state.fields:
        lines.append(f"    {field}: any  # À initialiser")
    lines.append("")  # ligne vide
    # Méthodes de transition
    for name, fn_name in state.transitions:
        lines.append(f"    def {fn_name}(self, *args, **kwargs):")
        lines.append(f"        \"\"\"Transition '{name}'\"\"\"")
        lines.append("        # TODO: implémenter préconditions et mises à jour d'état")
        lines.append("        pass")
        lines.append("")  # ligne vide entre méthodes
    return "\n".join(lines)
