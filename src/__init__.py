from os import path

CHEMIN = path.abspath(path.split(__file__)[0])  # Récuperation du chemin ou est le fichier
CHEMINOTHERS = path.abspath(CHEMIN + "/../others//")  # Chemin du dossier others
