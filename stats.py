from os import path
import json

chemin = path.abspath(path.split(__file__)[0])  # Récuperation du chemin ou est le fichier
cheminDATA = chemin + "/data/"  # Chemin faire le fichier data


# Les games comptées seront uniquement les solo/duos non remakes
def save_stat(data):
    if data is not None:
        with open(cheminDATA + "stats.json", 'w') as file:
            json.dump(data, file)

    print("Données sauvegardées")


def load_stat():
    data = {}
    try:
        with open(cheminDATA + "stats.json", 'rb') as file:
            data = json.load(file)
        print("Données chargées")
    except:
        save_stat({"nb_game_jours": 0, "nb_jours": 1, "nb_game_moyen_jours": 0})
        print("Fichier données créé")

    return data


def nouvelle_game(data):
    data["nb_game_jours"] += 1
    save_stat(data)



