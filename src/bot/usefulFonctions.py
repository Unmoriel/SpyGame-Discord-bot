import time

import requests
from numpy import concatenate
from PIL import Image
from matplotlib.image import imsave
from src.configuration import config
import cloudinary.uploader
import cloudinary.api
from src import CHEMIN, CHEMINDATA, CHEMINOTHERS

PATCH_DEFAULT = "14.3.1"  # Patch par défaut


def new_patch():
    requete = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if requete.status_code == 200:
        dernier_patch = requete.json()[0]
        return dernier_patch
    else:
        return PATCH_DEFAULT


def link_champions_data():
    return f"https://ddragon.leagueoflegends.com/cdn/{new_patch()}/data/fr_FR/champion.json"


def link_image_champion()-> str:
    return f"https://ddragon.leagueoflegends.com/cdn/{new_patch()}/img/champion/"


def getChampionsId(key):
    '''
    Au début j'utilisais la catégoris "championName" mais malheursement elle n'est pas présente
    dans les requetes des matchs en cours donc il me faut passer par leurs 'key' puis leur id
    (qui est enfaite leurs nom oui oui c'est bizarre)
    '''
    url_champions_data = link_champions_data()
    r = requests.get(url_champions_data)
    champions_data = r.json()['data']
    for champion in champions_data:
        if int(champions_data[champion]['key']) == key:
            return champions_data[champion]['id']


async def crea_image(participants, type_partie):
    url_champions_data, url_champions_image = link_champions_data(), link_image_champion()
    champions_data = requests.get(url_champions_data).json()['data']

    image = Image.open(
        requests.get(url_champions_image + champions_data[participants[0]['championName']]['image']['full'],
                     stream=True).raw)
    for i in range(1, len(participants)):
        req = requests.get(
            url_champions_image + champions_data[participants[i]['championName']]['image']['full'],
            stream=True).raw

        imagePlus = Image.open(req)
        image = concatenate((image, imagePlus), axis=1)
        if type_partie == "an Arena":
            if (i-1) % 2 == 0 and i != 7:
                imageArena = Image.open(CHEMINOTHERS + '/versus_white.jpg')
                image = concatenate((image, imageArena), axis=1)
        else:
            if i == 4:
                imageVersus = Image.open(CHEMINOTHERS + '/versus_white.jpg')
                image = concatenate((image, imageVersus), axis=1)

    return image


async def save_image_cloud(image):
    cloudinary.config(
        cloud_name=config.get_cloudinary_key()['cloud_name'],
        api_key=config.get_cloudinary_key()['api_key'],
        api_secret=config.get_cloudinary_key()['api_secret'],
        secure=True
    )
    imsave(CHEMINOTHERS+"/assembled_image.png", image)
    cloudinary.uploader.upload(CHEMINOTHERS+ "/assembled_image.png",
                               public_id="assembled_image", overwrite=True,
                               resource_type="image")
    return cloudinary.api.resource("assembled_image")["url"]


def str_rank(old_rank: dict, new_rank: dict, win: bool)-> str:
    text_lp = "\n"

    # If the player has no rank yet
    if old_rank["LP"] is None:
        text_lp += new_rank["tier"] + " " + new_rank["rank"] + " - " + str(new_rank["LP"]) + " LP"
        return text_lp

    change_rank = new_rank["tier"] != old_rank["tier"] or new_rank["rank"] != old_rank["rank"]
    # If the player has changed rank
    if change_rank:
        text_lp += "Promoted " if win else "Demoted "
        text_lp += (f"{old_rank['tier']} {old_rank['rank']} {old_rank['LP']} -> "
                   f"{new_rank['tier']} {new_rank['rank']} - {new_rank['LP']} LP")
        return text_lp

    # If the player has just won or lost LP
    lp_difference = abs(new_rank["LP"] - old_rank["LP"])
    text_lp += "LP : "
    text_lp += " + " if win else " - "
    text_lp += f"{lp_difference} LP ({new_rank['tier']} {new_rank['rank']} - {new_rank['LP']} LP)"

    return text_lp


def game_type(queue_id):
    url = "https://static.developer.riotgames.com/docs/lol/queues.json"
    requete = requests.get(url)
    if requete.status_code == 200:
        for queue in requete.json():
            if queue['queueId'] == queue_id:
                return queue['description']
        return "__Unknown__"
    else:
        print(f"Erreur : {requete.status_code} {requete.json()['status']['message']}")
        return "__Unknown__"

