import discord
from discord.ext import commands, tasks
from os import path
import requests
import pickle as pic

chemin = path.abspath(path.split(__file__)[0])  #Récuperation du chemin ou est le fichier
api_key = ""


def save_data(puuidDict, dernier_matchDict):
    with open(chemin+"/data.bin", "ab") as fichier_data:
        pic.dump([puuidDict, dernier_matchDict], fichier_data)

def load_data():
    with open(chemin+"/data.bin", "rb") as fichier_data:
        puuidDict, dernier_matchDict = pic.load(fichier_data)[0], pic.load(fichier_data)[1]
    return puuidDict, dernier_matchDict


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
                text += "Défaite\n"
    return text
            
def main():
    # Créer une instance du bot
    bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

    puiidDict = {} # {pseudo : puuid}
    dernier_matchDict = {} # {puuid : dernier_match}

    # Événement d'initialisation du bot
    @bot.event
    async def on_ready():
        print(f'Connecté en tant que {bot.user.name}')

        try:
            puuidDict, dernier_matchDict = load_data()
            print("Fichier de données chargé")
        except:
            save_data(puuidDict, dernier_matchDict)
            print("Fichier de données créé")

        cherche_derniers_match.start()

    # Commande personnalisée
    @bot.command()
    async def ajout(ctx, pseudo):
        puuidDict, dernier_matchDict = load_data()
        if pseudo in puuidDict.keys():
            await ctx.send("Ce pseudo est déjà enregistré")
        else:
            url_sumoner = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{pseudo}?api_key={api_key}"
            response = requests.get(url_sumoner)
            if response.status_code == 200:
                puuidDict[pseudo] = response.json()["puuid"]
                url_dernierMatch =  f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{response.json()['puuid']}/ids?start=0&count=1&api_key={api_key}"
                response_drMatch = requests.get(url_dernierMatch)
                if response_drMatch.status_code == 200:
                    dernier_matchDict[puuidDict[pseudo]] = response_drMatch.json()[0]
                    await ctx.send(pseudo + " a bien été ajouté")
                    save_data(puuidDict, dernier_matchDict)
                else:
                    await ctx.send("Erreur lors de la requête du dernier match : " + str(response.status_code))
            else:
                await ctx.send("Erreur lors de la requête du pseudo : " + str(response.status_code))

    @bot.command()
    async def supprimer(ctx, pseudo):
        puuidDict, dernier_matchDict = load_data()
        if pseudo in puuidDict.keys():
            del puuidDict[pseudo]
            await ctx.send(pseudo + " a bien été supprimé")
            save_data(puuidDict, dernier_matchDict)
        else:
            await ctx.send("Ce pseudo n'est pas enregistré")

    @bot.command()
    async def liste(ctx):
        puuidDict, dernier_matchDict = load_data()
        text = ""
        for pseudo in puuidDict.keys():
            text += pseudo + "\n"
        if(text == ""):
            text = "Aucun pseudo enregistré"
        await ctx.send(text)
    
        

    @tasks.loop(seconds=10)
    async def cherche_derniers_match():
        for puuid, dernier_match in dernier_matchDict.items():
            url_dernierMatch =  f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=1&api_key={api_key}"
            response = requests.get(url_dernierMatch)
            if response.status_code == 200:
                
                if dernier_match != response.json()[0]:
                    url_dernierMatchDiff = f"https://europe.api.riotgames.com/lol/match/v5/matches/{response.json()[0]}?api_key={api_key}"
                    response2 = requests.get(url_dernierMatchDiff)
                    
                    if response2.status_code == 200:
                        channel = discord.utils.get(bot.get_all_channels(), type=discord.ChannelType.text)
                        await channel.send(match_text())
                        dernier_matchDict[puuid] = response.json()[0]
                    else:
                        print("Erreur lors de la requête du dernier match différent : " + str(response.status_code))
                
                else:
                    print("Pas de nouveau match")
            else:
                print("Erreur lors de la requête du dernier match : " + str(response.status_code))
        


    bot.run('')

main()