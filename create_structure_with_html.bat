# Génération du script batch Windows mis à jour pour inclure les fichiers HTML
script = r"""@echo off
REM Script pour créer l'arborescence de baten_chess en Windows CMD
REM Placez ce fichier dans le dossier 'baten_chess' et exécutez-le depuis cmd

pushd "%~dp0"

REM Création des dossiers
mkdir baten_chess_engine
mkdir tests
mkdir templates
mkdir static
mkdir static\css

REM Création des fichiers Python de base
type nul > baten_chess_engine\__init__.py
type nul > baten_chess_engine\board.py
type nul > baten_chess_engine\validator.py
type nul > baten_chess_engine\engine.py
type nul > tests\test_validator.py

REM Création des fichiers HTML et CSS
type nul > templates\board.html
type nul > static\css\style.css

echo Structure de projet (avec HTML/CSS) créée avec succès.
pause
"""

# Écriture du script dans /mnt/data
file_path = '/mnt/data/create_structure_with_html.bat'
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(script)

print(f"Script batch Windows amélioré généré : [Télécharger create_structure_with_html.bat]({file_path})")
