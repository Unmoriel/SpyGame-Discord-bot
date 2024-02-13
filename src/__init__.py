from os import path

CHEMIN = path.abspath(path.split(__file__)[0])  # Récuperation du chemin ou est le fichier
CHEMINDATA = path.abspath(CHEMIN + "/../data//")  # Chemin du dossier data
CHEMINOTHERS = path.abspath(CHEMIN + "/../others//")  # Chemin du dossier others
