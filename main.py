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
            queueId = data["info"]["queueId"]
            text += "Type de partie : "
            if queueId == 420:
                text += "Ranked\n"
            elif queueId == 430:
                text += "Normal Blind\n"
            elif queueId == 400:
                text += "Normal Draft\n"
            elif queueId == 450:
                text += "ARAM\n"
            elif queueId == 440:
                text += "Flex\n"
            elif queueId == 31 or queueId == 32 or queueId == 33:
                text += "Coop vs IA\n"
            else:
                text += queueId+" inconnue\n"
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

    @bot.event
    async def on_message(message):
        if message.content == '!embed':
            embed = discord.Embed(
            title='Unmoriel win',
            color=0xFF0000,
            )
            embed.add_field(
                name='Ranked - 7/12/3',
                value='Bref',
                inline=True
            )
            embed.set_thumbnail(url="http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/DrMundo.png")
            # Ajouter plusieurs images à l'embed
            embed.set_image(url="http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/DrMundo.png")
            embed.add_field(
                name="Champ 1",
                value="Contenu du champ 1",
                inline=False
            )
            embed.set_image(url="http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/Amumu.png")
            embed.add_field(
                name="Champ 2",
                value="Contenu du champ 2",
                inline=False
            )
            embed.set_image(url="http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/DrMundo.png")
            embed.add_field(
                name="Champ 3",
                value="Contenu du champ 3",
                inline=False
            )



            await message.channel.send(embed=embed)
    

    
        
    '''
    All 10 seconds, check if the last match of each player is same as stored in the dictionnary
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
                        queueId = response2.json()["info"]["queueId"]
                        print(queueId)
                        type_partie = "" 
                        if queueId == 420:
                            type_partie += "Solo/Duo"
                        elif queueId == 430:
                            type_partie += "Normal Blind"
                        elif queueId == 400:
                            type_partie += "Normal Draft"
                        elif queueId == 450:
                            type_partie += "ARAM"
                        elif queueId == 440:
                            type_partie += "Flex"
                        elif queueId == 31 or queueId == 32 or queueId == 33:
                            type_partie += "Coop vs IA"
                        else:
                            text += queueId+" inconnue\n"

                        for participant in response2.json()["info"]["participants"]:
                            if participant["puuid"] == puuid:
                                 
                                embed = discord.Embed(
                                        title=participant["summonerName"] + " " + ("win" if participant["win"] else "lose") + " a " + type_partie,
                                        color=0xFF0000,
                                )
                                embed.add_field(
                                        name= participant["championName"] + " - " + str(participant["kills"]) + "/" + str(participant["deaths"]) + "/" + str(participant["assists"]),
                                        value='',
                                        inline=True
                                )
                                embed.set_thumbnail(
                                    url=f"http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/{participant['championName']}.png"
                                )
                        await channel.send(embed=embed)
                        dernier_matchDict[puuid] = response.json()[0]
                        save_data(puuidDict, dernier_matchDict)
                    else:
                        print("Erreur lors de la requête du dernier match différent : " + str(response.status_code))
                
                else:
                    print("Pas de nouveau match")
            else:
                print("Erreur lors de la requête du dernier match : " + str(response.status_code))
        
    bot.run(discord_k)
print(cheminDATA)
main()