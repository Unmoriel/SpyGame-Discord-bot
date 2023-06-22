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


chemin = path.abspath(path.split(__file__)[0])  #Récuperation du chemin ou est le fichier
cheminDATA = path.dirname(chemin) + "/data/"

'''
Return the api key (first riot, secondly discord) from the a json file (in local)
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
This time files are store in local not in the git repository
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
            puuidDict = data["puuidDict"]
            dernier_matchDict = data["dernier_matchDict"]
            channel = data['channel']
            print("Données chargées")
            return puuidDict, dernier_matchDict, channel
    except:
        save_data({}, {}, -1)
        print("Fichier données créé")
        return {}, {}, -1

'''
Save data in the json file
'''
def save_data(puuidDict, dernier_matchDict, channel_id):
    with open(cheminDATA + "data.json", 'w') as file:
        json.dump({"puuidDict":puuidDict, "dernier_matchDict":dernier_matchDict, "channel" : channel_id}, file)
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
    puuidDict = {} # {pseudo : puuid}
    dernier_matchDict = {} # {puuid : dernier_match}
    channel_id = -1 # Channel id where the bot will send the message     
    puuidDict, dernier_matchDict, channel_id = load_data()
    
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
        save_data(puuidDict, dernier_matchDict, channel_id)

    # Remove a player from the dictionnary
    @bot.command()
    async def remove(ctx, pseudo):
        if pseudo in puuidDict.keys():
            del puuidDict[pseudo]
            del dernier_matchDict[puuidDict[pseudo]]
            await ctx.send(pseudo + " a bien été supprimé")
        else:
            await ctx.send("Ce pseudo n'est pas enregistré")
        save_data(puuidDict, dernier_matchDict, channel_id)

    # Show the list of players who are watched
    @bot.command()
    async def list(ctx):
        text = ""
        for pseudo in puuidDict.keys():
            text += pseudo + "\n"
        if(text == ""):
            text = "Aucun pseudo enregistré"
        await ctx.send(text)        
    
    # Change the channel where the bot will send the image
    @bot.command()
    async def here(ctx):
        channel = ctx.channel
        channel_id = channel.id
        await ctx.send("Le channel de notification est maintenant " + channel.name)
        save_data(puuidDict, dernier_matchDict, channel_id)

    '''
    All 10 seconds, check if the last match of each player is same as stored in the dictionnary
    If it's not the same, send a embed message in the discord 
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
                    if channel_id == -1:
                        channel = discord.utils.get(bot.get_all_channels(), type=discord.ChannelType.text)
                    else:
                        channel = bot.get_channel(channel_id)
                    
                    if response2.status_code == 200:
                        queueId = response2.json()["info"]["queueId"]
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
                        
                        pseudo = ''

                        for participant in response2.json()["info"]["participants"]:
                            if participant["puuid"] == puuid:
                                pseudo = participant["summonerName"]
                                embed = discord.Embed(
                                        title=participant["summonerName"] + " " + ("win" if participant["win"] else "lost") + " " + type_partie,
                                        color=0xFF0000,
                                )
                                embed.add_field(
                                        name= participant["championName"] + " - " + str(participant["kills"]) + "/" + str(participant["deaths"]) + "/" + str(participant["assists"]),
                                        value= "CS : "+ str(participant["totalMinionsKilled"]) + " - " + str(participant["goldEarned"]) + " golds",
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
                        
                        await channel.send(embed=embed)
                        dernier_matchDict[puuid] = response.json()[0]
                        print("Nouveau match pour "+pseudo)
                        save_data(puuidDict, dernier_matchDict, channel_id)
                    else:
                        print("Erreur lors de la requête du dernier match différent : " + str(response.status_code))
                
                else:
                    print("Pas de nouveau match")
            else:
                print("Erreur lors de la requête du dernier match : " + str(response.status_code))
        
    bot.run(discord_k)
main()