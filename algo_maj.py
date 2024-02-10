from os import path
import json

chemin = path.abspath(path.split(__file__)[0])  #Récuperation du chemin ou est le fichier
cheminDATA = chemin + "/data/" #Chemin faire le fichier data

"""
Update the data structur
"""
def to_1_0():
    with open(cheminDATA+"data.json", "rb") as file:
        data = json.load(file)

    for pseudo in data.keys():
        data[pseudo].pop('LP')
        data[pseudo].pop('tier')
        data[pseudo].pop('rank')
        data[pseudo].pop('matchEnCours')
        
        data[pseudo]['win_total'] = 0
        data[pseudo]['win_week'] = 0
        data[pseudo]['loose_total'] = 0
        data[pseudo]['loose_week'] = 0
        data[pseudo]['RANKED_FLEX_SR'] = {"LP": None, "rank": None, "tier": None}
        data[pseudo]['RANKED_SOLO_5x5'] = {"LP": None, "rank": None, "tier": None}
        
        data[pseudo]['dernierMatch'] = "0"
    
    with open(cheminDATA+"data.json", "w") as file:
        json.dump(data, file)


to_1_0()
