import discord
from discord.ext import tasks
from os import path
import cloudinary
import cloudinary.uploader
import cloudinary.api
from discord.ui.item import Item
from matplotlib.image import imread, imsave
from numpy import concatenate 
from PIL import Image
import requests
import json
import datetime
import asyncio
from collections import OrderedDict

chemin = path.abspath(path.split(__file__)[0])  #Récuperation du chemin ou est le fichier
cheminDATA = path.dirname(chemin) + "/data/"
urlChampionsData = "https://ddragon.leagueoflegends.com/cdn/13.13.1/data/en_US/champion.json"
urlChamionsImage = "http://ddragon.leagueoflegends.com/cdn/13.13.1/img/champion/"


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

def getChampionsId(key):
    r = requests.get(urlChampionsData)
    championsData = r.json()['data']
    for champion in championsData:
        if int(championsData[champion]['key']) == key:
            return championsData[champion]['id']


'''
Create the image with all the champions of the game
'''
def crea_Image(participant):
    championsData = requests.get(urlChampionsData).json()['data']
    
    image = Image.open(requests.get(urlChamionsImage+championsData[getChampionsId(participant[0]['championId'])]['image']['full'], stream=True).raw)
    for i in range(1, len(participant)):
        req = requests.get(urlChamionsImage+championsData[getChampionsId(participant[i]['championId'])]['image']['full'], stream=True).raw
        imagePlus = Image.open(req)
        image = concatenate((image, imagePlus), axis=1)
        if i == 4:
            imageVersus = Image.open(cheminDATA+'/others/versus_white.jpg')
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
    elif queueId == 31 or queueId == 32 or queueId == 33:
        type_partie += "a Coop vs IA"
    else:
        type_partie += str(queueId)+" __inconnue__\n"
    
    return type_partie

'''
Load data from the json file
If he doesn't exist, create it
'''
def load_data():
    try:
        with open(cheminDATA + "data.json", 'rb') as file:
            data = json.load(file)
        with open(cheminDATA + "dataDiscord.json", "rb") as file:
            dataD = json.load(file)
        print("Données chargées")
        return data, dataD
    
    except:
        data = {}
        dataD =  {'parisEnCours' : {}, 'discordUser' : {}, 'channel' : None}
        save_data({}, dataD)
        print("Fichier données créé")
        return {}, dataD

'''
Save data in the json file
Default is set on None if you want save only one file
'''
def save_data(puuidDict = None, dataD = None):
    
    if puuidDict != None:
        with open(cheminDATA + "data.json", 'w') as file:
                json.dump(puuidDict, file)

    if dataD != None :
        with open(cheminDATA + "dataDiscord.json", 'w') as file:
            json.dump(dataD, file)
    
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

    
    bot = discord.Bot()

    # Dictionnary where data of players are stored (in local)
    puuidDict, dataD = load_data() # puuidDict = {pseudo : {'puuid' : puuid, 'summonerId' : summonerId 'dernierMatch' : dernierMatch, 'channel' : channel_id, 'LP' : LP,
                            #  'rank' : rank, 'tier' : tier, 'matchEnCours' : gameId}}
                            # dataD = {'parisEnCours' : {}, 'discordUser' : {}, 'channel' : int}
    
    parisEnCours = dict(dataD['parisEnCours'])# {'gameId' : {'Win' : [], 'Loose' : []}}
    discordUser = dict(dataD['discordUser']) # {'userId' : {'name' : str, 'nbWin' : int, 'nbDef' : int}}
    channelParis = dataD['channel'] #int

    
    # When the discord bot is ready
    @bot.event
    async def on_ready():
        look_for_last_match.start()
        look_for_started_match.start()
        print(f'Connecté en tant que {bot.user.name}')


    
    @bot.event
    async def parier(interaction : discord.Interaction, button : discord.ui.Button, gameId : int, pseudo : str):
        if interaction.user.id in parisEnCours[gameId]['Win'] :
            await interaction.response.send_message("Vous avez déjà voté 'Win' pour ce paris !", ephemeral=True)
        elif interaction.user.id in parisEnCours[gameId]['Loose']:
            await interaction.response.send_message("Vous avez déjà voté 'Loose' pour ce paris !", ephemeral=True)
        else:
            if not(interaction.user.id in discordUser.keys()):
                discordUser[interaction.user.id] = {'name' : interaction.user.display_name, 'nbWin' : 0, 'nbDef' : 0}
            
            parisEnCours[gameId][button.label].append(interaction.user.id)      
            dataD['parisEnCours'] = parisEnCours
            dataD['discordUser'] = discordUser
            save_data(dataD=dataD)
            await interaction.response.send_message(interaction.user.name +" a voté pour que "+pseudo+" "+button.label)
            
    
    @bot.event
    async def parisFini(pseudo : str, win : bool, gameId : int):
        if gameId not in parisEnCours.keys():
            print(f'Paris {gameId} non trouvé')
            return None
        
        perdantL = []
        gagnantL = []
        if win:
            gagnantL = parisEnCours[gameId]['Win']
            perdantL = parisEnCours[gameId]['Loose']
        else:
            gagnantL = parisEnCours[gameId]['Loose']
            perdantL = parisEnCours[gameId]['Win']
        
        text_gagnant = ""
        text_perdant = ""
        for gagnant in gagnantL:
            user = await bot.fetch_user(gagnant)
            text_gagnant += user.display_name+"\n"
            discordUser[gagnant]["nbWin"] += 1
        
        for perdant in perdantL:
            user = await bot.fetch_user(perdant)
            text_perdant += user.display_name+"\n"
            discordUser[perdant]["nbDef"] += 1
        
        embed = discord.Embed(
            title="Paris terminé !",
            description=f"{pseudo} a "+ ("gagné" if win else "perdu") + " sa partie !",
            color= discord.Color.yellow()
        )
        embed.add_field(
            name="Gagnant(s)",
            value=text_gagnant,
            inline=True
        )
        embed.add_field(
            name= "Perdant(s) :",
            value= text_perdant,
            inline=True
            )
        embed.timestamp = datetime.datetime.now()
        await bot.get_channel(discordUser["channel"]).send(embed=embed)
        del parisEnCours[gameId]
        
            
    
    class ViewParis(discord.ui.View): 

        
        def __init__(self, *items: Item, timeout: float | None = 180, disable_on_timeout: bool = False, gameId : int, pseudo : str):
            super().__init__(*items, timeout=timeout, disable_on_timeout=disable_on_timeout)
            self.gameId = gameId
            self.pseudo = pseudo
            
    
        @discord.ui.button(label="Loose", style=discord.ButtonStyle.primary)
        async def button_callback(self, button, interaction):
            await parier(interaction, button, self.gameId, self.pseudo)
        
        @discord.ui.button(label="Win", style=discord.ButtonStyle.primary)
        async def button2_callback(self, button, interaction):
            await parier(interaction, button, self.gameId, self.pseudo)
        
        async def on_timeout(self):
            self.disable_all_items()
            await self.message.edit(content="Le paris est fermé", view=self)


    @bot.command()
    async def clear_paris(ctx : discord.ApplicationContext):
        if await bot.is_owner(ctx.user):
            parisEnCours.clear()
            dataD['parisEnCours'] = parisEnCours
            save_data(dataD=dataD)
            await ctx.respond("Les paris en cours ont été supprimé")
        else:
            await ctx.respond("Vous n'avez pas les droits")
        
    @bot.command()
    async def test(ctx : discord.ApplicationContext):
        user = await bot.fetch_user(244758152858304514)
        await ctx.respond(user.display_name) 
    
    @bot.command()
    async def leaderboard(ctx : discord.ApplicationContext):
        text_l = ""
        for parieur in discordUser.keys():
            text_l += discordUser[parieur]["name"] + "\n"
        
        if text_l == "":
            await ctx.respond("Aucun parieurs enregistré")
        else:
            await ctx.respond(text_l)
        
        
    @bot.command()
    async def paris_here(ctx):
        dataD['channel'] = ctx.channel_id
        save_data(dataD=dataD)
        await ctx.respond("Les paris seront envoyé dans ce channel")
       
    @bot.command(description="Sends the bot's latency.") 
    async def ping(ctx): 
        await ctx.respond(f"Pong! Latency is : {bot.latency}")
    
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
                                             'tier' : response_rang.json()[0]['tier'],
                                             'matchEnCours' : 0
                                            }
                        
                        await ctx.respond(pseudo + " a bien été ajouté")
                    else:
                        await ctx.respond("Erreur lors de la requête du rang : " + str(response_rang.status_code))
                else:
                    await ctx.respond("Erreur lors de la requête du dernier match : " + str(response.status_code))
            else:
                await ctx.respond("Erreur lors de la requête du pseudo : " + str(response.status_code))
        save_data(puuidDict)
    
    '''
    Permet l'autocompletion du paramètre pseudo dans la slashCommand remove
    '''
    async def get_pseudo_remove(ctx : discord.AutocompleteContext):
        
        l = []
        for pseudo in puuidDict.keys():
            l.append(pseudo)
        
        return l
            
    # Remove a player from the dictionnary
    @bot.slash_command(name="remove")
    async def remove(ctx : discord.ApplicationContext, pseudo : discord.Option(str, autocomplete=discord.utils.basic_autocomplete(get_pseudo_remove))):
        if pseudo in puuidDict.keys():
            del puuidDict[pseudo]
            await ctx.respond(pseudo + " a bien été supprimé")
        else:
            await ctx.respond("Ce pseudo n'est pas enregistré")
        save_data(puuidDict)

    # Show the list of players who are watched
    @bot.command()
    async def list(ctx):
        text = ""
        for pseudo in puuidDict.keys():
            text += pseudo + "\n"
        if(text == ""):
            text = "Aucun pseudo enregistré"
        await ctx.respond(text)        

    '''
    All 10 seconds, check if the last match of each playcer is same as stored in the dictionnary
    If it's not the same, send a embed message in the discord 
    and update the dictionnary
    '''
    @tasks.loop(seconds=10.0)
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
                            gameId = response2.json()["info"]['gameId']
                            type_partie = gameType(queueId)
                            win = False
                            

                            for participant in response2.json()["info"]["participants"]:
                                if participant["puuid"] == puuidDict[pseudo]["puuid"]:
                                    win = participant["win"]
                                    
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
                                            if win:
                                                text_LP += f"LP : +{lp_Difference}"
                                            else:
                                                text_LP += f"LP : -{lp_Difference}"
                                            
                                            text_LP += f" ({puuidDict[pseudo]['tier']} {puuidDict[pseudo]['rank']} - {response_newRank.json()[0]['leaguePoints']} LP)"
                                        
                                        puuidDict[pseudo]['LP'] = response_newRank.json()[0]['leaguePoints']
                                        
                                                
                                    embed = discord.Embed(
                                            title=participant["summonerName"] + " " + ("won" if win else "lost") + " " + type_partie,
                                            color=discord.Color.green() if participant["win"] else discord.Color.red()
                                    )
                                    embed.add_field(
                                        name= participant["championName"] + " - " + str(participant["kills"]) + "/" + str(participant["deaths"]) + "/" + str(participant["assists"]),
                                        value= "CS : "+ str(participant["neutralMinionsKilled"]) + " - " + str(participant["goldEarned"]) + " golds" + text_LP,
                                        inline=True
                                    )
                                    embed.set_thumbnail(
                                        url=f"http://ddragon.leagueoflegends.com/cdn/13.13.1/img/champion/{participant['championName']}.png"
                                    )
                                    embed.timestamp = datetime.datetime.now()
                                
                            gameChampImage = crea_Image(response2.json()["info"]["participants"])
                            imsave(cheminDATA+"temp/assembled_image.png", gameChampImage)
                            #I must upload the image to cloudinary to get the url because discord doesn't accept local image
                            cloudinary.uploader.upload(cheminDATA+"temp/assembled_image.png", public_id = "assembled_image", overwrite = True, resource_type = "image")
                            embed.set_image(url=cloudinary.api.resource("assembled_image")["url"])
                            
                            await bot.get_channel(puuidDict[pseudo]['channel']).send(embed=embed)
                            if gameId == puuidDict[pseudo]['matchEnCours']:
                                await parisFini(pseudo, win, gameId)
                            
                            puuidDict[pseudo]['dernierMatch'] = response.json()[0]
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
        
        
    @tasks.loop(seconds=13)
    async def look_for_started_match():
        for pseudo in puuidDict.keys():
            reponse = requests.get(f"https://euw1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{puuidDict[pseudo]['summonerId']}?api_key={riot}")
            if reponse.status_code == 200:
                if puuidDict[pseudo]['matchEnCours'] != reponse.json()['gameId']:
                    print(f"{pseudo} à lancé une partie")
                    print("lancement du paris")
                    participants = reponse.json()['participants']
                    gameChampPourParis = crea_Image(participants)
                    imsave(cheminDATA+"temp/assembled_image.png", gameChampPourParis)
                    cloudinary.uploader.upload(cheminDATA+"temp/assembled_image.png", public_id = "assembled_image_paris", overwrite = True, resource_type = "image")
                    for participant in participants:
                        if participant["summonerId"] == puuidDict[pseudo]['summonerId']:
                            embed = discord.Embed(
                                    title=participant["summonerName"] + " start " + gameType(reponse.json()['gameQueueConfigId']),
                                    color=discord.Color.blue()
                                )
                            embed.add_field(
                                    name= "Faites vos paris !",
                                    value= f"{pseudo} est {puuidDict[pseudo]['tier']} {puuidDict[pseudo]['rank']} {puuidDict[pseudo]['LP']} LP"
                                )
                            embed.set_thumbnail(
                                    url=f"http://ddragon.leagueoflegends.com/cdn/13.13.1/img/champion/{getChampionsId(participant['championId'])}.png"
                                )
                            embed.timestamp = datetime.datetime.now()
                            embed.set_image(url=cloudinary.api.resource("assembled_image_paris")["url"])
                    
                    puuidDict[pseudo]['matchEnCours'] = reponse.json()['gameId']
                    if channelParis != None:
                        parisEnCours[reponse.json()['gameId']] = {'Win' : [], 'Loose' : []} #Création du paris
                        await bot.get_channel(discordUser['channel']).send(embed=embed, view=ViewParis(timeout=300, gameId=reponse.json()['gameId'], pseudo=pseudo))

                    save_data(puuidDict) #Je ne sauvegarde pas le paris tout de suite
                else:
                    print(f"Paris déjà lancé pour {pseudo}")
            else:
                if(reponse.status_code == 400):
                    print(reponse.json())
                else:
                    print(f'Pas de paris à faire ({reponse.status_code})')

    bot.run(discord_k)
main()