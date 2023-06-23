import discord
from discord.ext import commands, tasks
from os import path
import cloudinary
import cloudinary.uploader
import cloudinary.api
from matplotlib.image import imread, imsave
from numpy import concatenate 
import requests
import json
import datetime
from time import sleep


chemin = path.abspath(path.split(__file__)[0])  #Récuperation du chemin ou est le fichier
cheminDATA = path.dirname(chemin) + "/data/"

'''
Return the api key from the a json file (in local)
which is not in the git repository (here it's in a folder named "data"
in the parent folder's project and his name is "apiKey.json")
'''
def get_api_key(riot, discord_k, cloudinary_k):
    with open(cheminDATA + "apiKey.json") as file:
        data = json.load(file)
        riot = data["riot"]
        discord_k = data["discord"]
        cloudinary_k = data["cloudinary"]
        return riot, discord_k, cloudinary_k

'''
Create the image with all the champions of the game
This time files are store in local
'''
def crea_Image(participant):

    image = imread(cheminDATA+'champion/tiles/'+participant[0]['championName']+'_0.jpg')
    for i in range(1, len(participant)):
        imagePlus = imread(cheminDATA+'champion/tiles/'+participant[i]['championName']+'_0.jpg')
        image = concatenate((image, imagePlus), axis=1)
        if i == 4:
            imageVersus = imread(cheminDATA+'others/versus_white.jpg')
            image = concatenate((image, imageVersus), axis=1)
    
    return image

'''
Load data from the json file
If he doesn't exist, create it
'''
def load_data():
    try:
        with open(cheminDATA + "data.json", 'rb') as file:
            data = json.load(file)
            print("Données chargées")
            return data
    except:
        save_data({})
        print("Fichier données créé")
        return {}

'''
Save data in the json file
'''
def save_data(puuidDict):
    with open(cheminDATA + "data.json", 'w') as file:
        json.dump(puuidDict, file)
        print("Données sauvegardées")
            

def main():
    riot, discord_k, cloudinary_k = '', '', {} # API keys, see get_api_key()
    riot, discord_k, cloudinary_k = get_api_key(riot, discord_k, cloudinary_k)

    cloudinary.config(
        cloud_name = cloudinary_k["cloud_name"],
        api_key = cloudinary_k["api_key"],
        api_secret = cloudinary_k["api_secret"],
        secure = True
    )


    bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

    # Dictionnary where data of players are stored (in local)
    puuidDict = load_data() # {pseudo : {'puuid' : puuid, 'summonerId' : summonerId 'dernierMatch' : dernierMatch, 'channel' : channel_id, 'LP' : LP,
                            #  'rank' : rank, 'tier' : tier}}
    
    
    
    
    # When the discord bot is ready
    @bot.event
    async def on_ready():
        print(f'Connecté en tant que {bot.user.name}')
        look_for_last_match.start()



    # Append a player in the dictionnary to watch him
    @bot.command()
    async def add(ctx, pseudo : str, channel : discord.TextChannel):
        if pseudo in puuidDict.keys():
            await ctx.send("Ce pseudo est déjà enregistré")
        else:
            response = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{pseudo}?api_key={riot}")
            if response.status_code == 200:
                response_drMatch = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{response.json()['puuid']}/ids?start=0&count=1&api_key={riot}")
                if response_drMatch.status_code == 200:
                    response_rang = requests.get(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{response.json()['id']}?api_key={riot}")
                    if response_rang.status_code == 200:
                        puuidDict[pseudo] = {'puuid' : response.json()['puuid'], 
                                             'summonerId' : response.json()['id'],
                                             'dernierMatch' : response_drMatch.json()[0], 
                                             'channel' : channel.id, 
                                             'LP' : response_rang.json()[0]['leaguePoints'], 
                                             'rank' : response_rang.json()[0]['rank'], 
                                             'tier' : response_rang.json()[0]['tier']
                                            }
                        
                        await ctx.send(pseudo + " a bien été ajouté")
                    else:
                        await ctx.send("Erreur lors de la requête du rang : " + str(response_rang.status_code))
                else:
                    await ctx.send("Erreur lors de la requête du dernier match : " + str(response.status_code))
            else:
                await ctx.send("Erreur lors de la requête du pseudo : " + str(response.status_code))
        save_data(puuidDict)

    # Remove a player from the dictionnary
    @bot.command()
    async def remove(ctx, pseudo):
        if pseudo in puuidDict.keys():
            del puuidDict[pseudo]
            await ctx.send(pseudo + " a bien été supprimé")
        else:
            await ctx.send("Ce pseudo n'est pas enregistré")
        save_data(puuidDict)

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
    All 10 seconds, check if the last match of each player is same as stored in the dictionnary
    If it's not the same, send a embed message in the discord 
    and update the dictionnary
    '''
    @tasks.loop(seconds=10)
    async def look_for_last_match():
        for pseudo in puuidDict.keys():
            response = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuidDict[pseudo]['puuid']}/ids?start=0&count=1&api_key={riot}")
            if response.status_code == 200:
                
                if puuidDict[pseudo]['dernierMatch'] != response.json()[0]: #if the last match is different
                    response2 = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{response.json()[0]}?api_key={riot}")
                    if response2.status_code == 200:
                        response_newRank = requests.get(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{puuidDict[pseudo]['summonerId']}?api_key={riot}")
                        if response_newRank.status_code == 200:
                            queueId = response2.json()["info"]["queueId"] #const wich define the type of game
                            
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
                            elif queueId == 31 or queueId == 32 or queueId == 33:
                                type_partie += "a Coop vs IA"
                            else:
                                text += queueId+" __inconnue__\n"
                            

                            for participant in response2.json()["info"]["participants"]:
                                if participant["puuid"] == puuidDict[pseudo]['puuid']:
                                    
                                    text_LP = ""
                                    if queueId == 420: #if it's a Solo/Duo
                                        text_LP += "\n"
                                        lp_Difference = abs(response_newRank.json()[0]['leaguePoints'] - puuidDict[pseudo]['LP'])
                                        changeRank = False
                                        
                                        if puuidDict[pseudo]['rank'] != response_newRank.json()[0]['rank'] :
                                            changeRank = True
                                            
                                        if changeRank:
                                            if participant["win"]:
                                                text_LP += f"Promote : {puuidDict[pseudo]['tier']} {puuidDict[pseudo]['rank']} -> {response_newRank.json()[0]['tier']} {response_newRank.json()[0]['rank']}"
                                            else:
                                                text_LP += f"Demote : {puuidDict[pseudo]['tier']} {puuidDict[pseudo]['rank']} -> {response_newRank.json()[0]['tier']} {response_newRank.json()[0]['rank']}"
                                            puuidDict[pseudo]['rank'] = response_newRank.json()[0]['rank']
                                            puuidDict[pseudo]['tier'] = response_newRank.json()[0]['tier']
                                             
                                        else:
                                            if participant["win"]:
                                                text_LP += f"LP : +{lp_Difference}"
                                            else:
                                                text_LP += f"LP : -{lp_Difference}"
                                        
                                        puuidDict[pseudo]['LP'] = response_newRank.json()[0]['leaguePoints']
                                        
                                                
                                    pseudo = participant["summonerName"]
                                    embed = discord.Embed(
                                            title=participant["summonerName"] + " " + ("won" if participant["win"] else "lost") + " " + type_partie,
                                            color=discord.Color.green() if participant["win"] else discord.Color.red()
                                    )
                                    embed.add_field(
                                            name= participant["championName"] + " - " + str(participant["kills"]) + "/" + str(participant["deaths"]) + "/" + str(participant["assists"]),
                                            value= "CS : "+ str(participant["neutralMinionsKilled"]) + " - " + str(participant["goldEarned"]) + " golds" + text_LP,
                                            inline=True
                                    )
                                    embed.set_thumbnail(
                                        url=f"http://ddragon.leagueoflegends.com/cdn/13.12.1/img/champion/{participant['championName']}.png"
                                    )
                                    embed.timestamp = datetime.datetime.now()
                                
                            gameChampImage = crea_Image(response2.json()["info"]["participants"])
                            imsave(cheminDATA+"temp/assembled_image.png", gameChampImage)
                            #I must upload the image to cloudinary to get the url because discord doesn't accept local image
                            cloudinary.uploader.upload(cheminDATA+"temp/assembled_image.png", public_id = "assembled_image", overwrite = True, resource_type = "image")
                            embed.set_image(url=cloudinary.api.resource("assembled_image")["url"])
                            
                            await bot.get_channel(puuidDict[pseudo]['channel']).send(embed=embed)
                            puuidDict[pseudo]['dernierMatch']= response.json()[0]
                            print("Nouveau match pour "+pseudo)
                            save_data(puuidDict)
                        else:
                            print("Erreur lors de la requête du nouveau rank : " + str(response_newRank.status_code))
                    else:
                        print("Erreur lors de la requête du dernier match différent : " + str(response.status_code))
                else:
                    print("Pas de nouveau match")
            else:
                print("Erreur lors de la requête du dernier match : " + str(response.status_code))
        
    bot.run(discord_k)
main()