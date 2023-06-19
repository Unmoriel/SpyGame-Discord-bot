import discord
from discord.ext import commands, tasks
from os import path
import requests
import json

chemin = path.abspath(path.split(__file__)[0])  #Récuperation du chemin ou est le fichier
cheminDATA = path.dirname(chemin) + "\\data\\"

'''
Return the api key (first riot, secondly discord) from the a json file (in local)
which is not in the git repository (here it's in a folder named "data"
in the parent folder's project and his name is "apiKey.json")
'''
def get_api_key(riot, discord_k):
    with open(cheminDATA + "apiKey.json") as file:
        data = json.load(file)
        riot = data["riot"]
        discord_k = data["discord"]
        return riot, discord_k

'''
Load data from the json file
If he doesn't exist, create it
'''
def load_data():
    try:
        with open(cheminDATA + "data.json", 'rb') as file:
            data = json.load(file)
            puuidDict = data["puuidDict"]
            dernier_matchDict = data["dernier_matchDict"]
            print("Données chargées")
            return puuidDict, dernier_matchDict
    except:
        save_data({}, {})
        print("Fichier données créé")
        return {}, {}

'''
Save data in the json file
'''
def save_data(puuidDict, dernier_matchDict):
    with open(cheminDATA + "data.json", 'w') as file:
        json.dump({"puuidDict":puuidDict, "dernier_matchDict":dernier_matchDict}, file)
        print("Données sauvegardées")

'''
Return the text to send in the discord channel
(When someone just win or loose a game)
'''
def match_text(data, puuid):
    text = ""
    for i in data["info"]["participants"]:
        if(i["puuid"] == puuid):
            text += "Pseudo : " + i["summonerName"] + "\n"
            text += "Type de partie : " + data["info"]["gameMode"] + "\n"
            text += "Champion : " + i["championName"] + "\n"
            text += "KDA : " + str(i["kills"]) + "/" + str(i["deaths"]) + "/" + str(i["assists"]) + "\n"
            if i["win"]:
                text += "Victoire\n"
            else:
                text += "Défaite (L)\n"
    return text
            

def main():
    riot, discord_k = '', '' # API keys, see get_api_key()
    riot, discord_k = get_api_key(riot, discord_k)

    bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

    # Dictionnary where data of players are stored (in local)
    puuidDict = {} # {pseudo : puuid}
    dernier_matchDict = {} # {puuid : dernier_match}

    # Load data from the json file
    puuidDict, dernier_matchDict = load_data()

    # When the discord bot is ready
    @bot.event
    async def on_ready():
        print(f'Connecté en tant que {bot.user.name}')
        look_for_last_match.start()

    # Append a player in the dictionnary to watch him
    @bot.command()
    async def add(ctx, pseudo):
        if pseudo in puuidDict.keys():
            await ctx.send("Ce pseudo est déjà enregistré")
        else:
            url_sumoner = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{pseudo}?api_key={riot}"
            response = requests.get(url_sumoner)
            if response.status_code == 200:
                puuidDict[pseudo] = response.json()["puuid"]
                url_dernierMatch =  f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{response.json()['puuid']}/ids?start=0&count=1&api_key={riot}"
                response_drMatch = requests.get(url_dernierMatch)
                if response_drMatch.status_code == 200:
                    dernier_matchDict[puuidDict[pseudo]] = response_drMatch.json()[0]
                    await ctx.send(pseudo + " a bien été ajouté")
                else:
                    await ctx.send("Erreur lors de la requête du dernier match : " + str(response.status_code))
            else:
                await ctx.send("Erreur lors de la requête du pseudo : " + str(response.status_code))
        save_data(puuidDict, dernier_matchDict)

    # Remove a player from the dictionnary
    @bot.command()
    async def remove(ctx, pseudo):
        if pseudo in puuidDict.keys():
            del puuidDict[pseudo]
            del dernier_matchDict[puuidDict[pseudo]]
            await ctx.send(pseudo + " a bien été supprimé")
        else:
            await ctx.send("Ce pseudo n'est pas enregistré")
        save_data(puuidDict, dernier_matchDict)

    # Show the list of players who are watched
    @bot.command()
    async def list(ctx):
        text = ""
        for pseudo in puuidDict.keys():
            text += pseudo + "\n"
        if(text == ""):
            text = "Aucun pseudo enregistré"
        await ctx.send(text)
    
        
    '''
    All 10 seconds, check if the last match of each player in the dictionnary is the same
    If it's not the same, send a message in the discord channel (see match_text()) 
    and update the dictionnary
    '''
    @tasks.loop(seconds=10)
    async def look_for_last_match():
        for puuid, dernier_match in dernier_matchDict.items():
            url_dernierMatch =  f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={riot}"
            response = requests.get(url_dernierMatch)
            if response.status_code == 200:
                
                if dernier_match != response.json()[0]:
                    url_dernierMatchDiff = f"https://europe.api.riotgames.com/lol/match/v5/matches/{response.json()[0]}?api_key={riot}"
                    response2 = requests.get(url_dernierMatchDiff)
                    
                    if response2.status_code == 200:
                        channel = discord.utils.get(bot.get_all_channels(), type=discord.ChannelType.text)
                        await channel.send(match_text(response2.json(), puuid))
                        dernier_matchDict[puuid] = response.json()[0]
                        save_data(puuidDict, dernier_matchDict)
                    else:
                        print("Erreur lors de la requête du dernier match différent : " + str(response.status_code))
                
                else:
                    print("Pas de nouveau match")
            else:
                print("Erreur lors de la requête du dernier match : " + str(response.status_code))
        
    bot.run(discord_k)

main()