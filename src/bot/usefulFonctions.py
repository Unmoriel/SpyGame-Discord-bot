import requests


def new_patch():
    requete = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if requete.status_code == 200:
        dernier_patch = requete.json()[0]
        urlChampionsData = f"https://ddragon.leagueoflegends.com/cdn/{dernier_patch}/data/en_US/champion.json"
        urlChamionsImage = f"http://ddragon.leagueoflegends.com/cdn/{dernier_patch}/img/champion/"

        return urlChampionsData, urlChamionsImage
    else:
        print("Erreur : Pas de patch trouvé")
        exit(1)


def crea_Image(participant, type_partie):
    championsData = requests.get(urlChampionsData).json()['data']

    image = Image.open(
        requests.get(urlChamionsImage + championsData[getChampionsId(participant[0]['championId'])]['image']['full'],
                     stream=True).raw)
    for i in range(1, len(participant)):
        req = requests.get(
            urlChamionsImage + championsData[getChampionsId(participant[i]['championId'])]['image']['full'],
            stream=True).raw
        imagePlus = Image.open(req)
        image = concatenate((image, imagePlus), axis=1)
        if type_partie == "an Arena":
            if (i-1) % 2 == 0 and i != 7:
                imageArena = Image.open(chemin + '/others/versus_white.jpg')
                image = concatenate((image, imageArena), axis=1)
        else:
            if i == 4:
                imageVersus = Image.open(chemin + '/others/versus_white.jpg')
                image = concatenate((image, imageVersus), axis=1)

    return image


def gameType(queueId):
    type_partie = ""
    if queueId == 420:
        type_partie += "a Solo/Duo"
    elif queueId == 430:
        type_partie += "a Normal Blind"
    elif queueId == 400:
        type_partie += "a Normal Draft"
    elif queueId == 450:
        type_partie += "an ARAM"
    elif queueId == 440:
        type_partie += "a Flex"
    elif queueId == 490:
        type_partie += "a quick game"
    elif queueId == 31 or queueId == 32 or queueId == 33:
        type_partie += "a Coop vs IA"
    elif queueId == 700:
        type_partie += "a Clash"
    elif queueId == 1700:
        type_partie += "an Arena"
    else:
        type_partie += f" __inconnue__ ({str(queueId)})"

    return type_partie

