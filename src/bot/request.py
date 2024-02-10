import requests
from src.configuration import conf

RIOT_API_KEY = conf.get_riot_key()


async def get_account(game_name: str, tag_line: str) -> dict:
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}?api_key={RIOT_API_KEY}"
    requete = requests.get(url)
    if requete.status_code == 200:
        puuid = requete.json()['puuid']
        requete2 = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={RIOT_API_KEY}")
        if requete2.status_code == 200:
            return requete2.json()
        else:
            print(f"Account Error : {requete2.status_code} {requete2.json()['status']['message']}")
            return {}
    else:
        print(f"Account Error : {requete.status_code} {requete.json()['status']['message']}")
        return {}


async def get_last_match(puuid: str) -> str:
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={RIOT_API_KEY}"
    requete = requests.get(url)
    if requete.status_code == 200:
        if len(requete.json()) == 0:
            return ""
        return requete.json()[0]
    else:
        print(f"Last match error : {requete.status_code} {requete.json()['status']['message']}")
        return ""


async def get_flex_rank(summonerId: str) -> dict:
    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={RIOT_API_KEY}"
    requete = requests.get(url)
    if requete.status_code == 200:
        for queue in requete.json():
            if queue['queueType'] == "RANKED_FLEX_SR":
                return {"tier": queue['tier'], "rank": queue['rank'], "LP": queue['leaguePoints']}
        return {}
    else:
        print(f"flex rank error : {requete.status_code} {requete.json()['status']['message']}")
        return {}


async def get_solo_rank(summonerId: str) -> dict:
    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={RIOT_API_KEY}"
    requete = requests.get(url)
    if requete.status_code == 200:
        for queue in requete.json():
            if queue['queueType'] == "RANKED_SOLO_5x5":
                return {"tier": queue['tier'], "rank": queue['rank'], "LP": queue['leaguePoints']}
        return {}
    else:
        print(f"solo rank error : {requete.status_code} {requete.json()['status']['message']}")
        return {}
