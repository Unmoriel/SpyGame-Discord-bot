from src.modele.repository import playerRepository, watchRepository, serverRepository
import json
import requests
from src.configuration import config
from sys import argv
import asyncio


async def pass_to_public_bot():
    """
    This function will take data from the last version of the bot and pass it to the public bot.
    In more details, the last version of the bot use "data.json" file to store data, the public bot use a real database,
    so this function will take the data from the .json file and put it in the database.
    :arg: name of the data.json file, the guild where players are stored
    """
    args = argv[1:]
    if len(args) != 2:
        print(f"Usage: {argv[0]} <data.json> <guild_id>")
        return

    try:
        await serverRepository.add_server(
            id_server=int(args[1])
        )
    except Exception as e:
        print("Error : ", e)

    riot = config.get_riot_key()
    with open(args[0], "rb") as file:
        data = json.load(file)

    for pseudo in data.keys():
        r = requests.get(f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/{data[pseudo]['puuid']}?api_key={riot}")
        if r.status_code == 200:
            await playerRepository.add_player(
                puuid=data[pseudo]['puuid'],
                game_name_tag_line=r.json()['gameName']+"#"+r.json()['tagLine'],
                sumonerId=data[pseudo]['summonerId'],
                pseudo=pseudo,
                dernier_match=data[pseudo]['dernierMatch'],
                loose_week=data[pseudo]['loose_week'],
                win_week=data[pseudo]['win_week'],
                rank_flex=data[pseudo]['RANKED_FLEX_SR'],
                rank_solo=data[pseudo]['RANKED_SOLO_5x5'],
            )
            await watchRepository.add_player_watch(
                puuid=data[pseudo]['puuid'],
                id_server=int(args[1])
            )
        else:
            print(f"{pseudo}\n{r.status_code}\n{r.text}")


asyncio.run(pass_to_public_bot())