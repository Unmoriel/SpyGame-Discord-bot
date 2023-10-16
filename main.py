import discord #Pycord
from discord.ext import tasks
from os import path
import cloudinary 
import cloudinary.uploader
import cloudinary.api
from matplotlib.image import imsave
from numpy import concatenate 
from PIL import Image
import requests
import json
import datetime
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler



chemin = path.abspath(path.split(__file__)[0])  #Récuperation du chemin ou est le fichier
cheminDATA = chemin + "/data/" #Chemin faire le fichier data 
version = "1.0"

def new_MAJ():
    try:
        old_version = ""
        with open(cheminDATA + "version.txt", 'rb') as file:
            old_version = file.read()
        
        if version == old_version.decode():
            print("Pas de MAJ")
            return False
        
        print("Erreur MAJ différente non prévue")
        exit(1)
    
    except:
        print("MAJ de la structur des données en 1.0")
        from algo_maj import to_1_0
        print("MAJ terminée")
        with open(cheminDATA + "version.txt", "w") as file:
            file.write(str(version))
        print("fichier de version créer")
        return True

        
            
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

urlChampionsData, urlChamionsImage = new_patch()

'''
Return the api key from the a json file (in local)
which is not in the git repository (here it's in a folder named "data" oui
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
Au début j'utilisais la catégoris "championName" mais malheursement elle n'est pas présente
dans les requetes des matchs en cours donc il me faut passer par leurs 'key' puis leur id
(qui est enfaite leurs nom oui oui c'est bizarre)
'''
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
            imageVersus = Image.open(chemin+'/others/versus_white.jpg')
            image = concatenate((image, imageVersus), axis=1)
    
    return image

'''
Riot game utilise des constantes pour leur mode de jeu.
Ici je transforme ces constantes en texte.
'''
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
    elif queueId == 700:
        type_partie += "a Clash"
    else:
        type_partie += f" __inconnue__ ({str(queueId)})"
    
    return type_partie

def crea_dict_player(rank : list, info : dict, last_match : str, channel_id):
    profil = {'puuid' : info['puuid'], 
            'summonerId' : info['id'],
            'dernierMatch' : last_match, 
            'channel' : channel_id, 
            'win_total' : 0,
            'win_week' : 0,
            'loose_total' : 0,
            'loose_week' : 0,
            'RANKED_FLEX_SR' : { 
                'LP' : None, 
                'rank' : None, 
                'tier' : None
                },
            'RANKED_SOLO_5x5' : {                                                        
                'LP' : None, 
                'rank' : None, 
                'tier' : None
                }
            }
    
    for queue in rank:
        profil[queue["queueType"]]["LP"] = queue["leaguePoints"]
        profil[queue["queueType"]]["rank"] = queue["rank"]
        profil[queue["queueType"]]["tier"] = queue["tier"]
            
 
    return profil
            
def update_rank(old_rank : dict, queue : dict, win : bool, queueType : str):
    text_LP = "\n"

    
    if old_rank[queueType]['LP'] is None :
        old_rank[queueType]['rank'] = queue['rank']
        old_rank[queueType]['tier'] = queue['tier']
        old_rank[queueType]['LP'] = queue['leaguePoints']
        text_LP += f"{queue['tier']} {queue['rank']} - {queue['leaguePoints']} LP"
        
    else :
        lp_Difference = abs(queue['leaguePoints'] - old_rank[queueType]['LP'])
        changeRank = False
                                            
        if old_rank[queueType]['rank'] != queue['rank'] :
            changeRank = True
                                                
        if changeRank:
            if win:
                text_LP += f"Promote : {old_rank[queueType]['tier']} {old_rank[queueType]['rank']} -> {queue['tier']} {queue['rank']}"
            else:
                text_LP += f"Demote : {old_rank[queueType]['tier']} {old_rank[queueType]['rank']} -> {queue['tier']} {queue['rank']}"
                old_rank[queueType]['rank'] = queue['rank']
                old_rank[queueType]['tier'] = queue['tier']
                old_rank[queueType]['LP'] = queue['leaguePoints']
                                                
        else:
            if win:
                text_LP += f"LP : +{lp_Difference}"
            else:
                text_LP += f"LP : -{lp_Difference}"
                                                
            text_LP += f" ({old_rank[queueType]['tier']} {old_rank[queueType]['rank']} - {queue['leaguePoints']} LP)"
                                            
            old_rank[queueType]['LP'] = queue['leaguePoints']

    return old_rank, text_LP
                
    

'''
Load data from the json file
If he doesn't exist, the function create it
'''
def load_data():
    data = {}
    discord_data = {}
    
    try:
        with open(cheminDATA + "data.json", 'rb') as file:
            data = json.load(file)
        print("Données chargées")
    except:
        save_data({})
        print("Fichier données créé")
        
    try:
        with open(cheminDATA + "discord_data.json", 'rb') as file:
            discord_data = json.load(file)
        print("Données discord chargées")
    except:
        save_data(discord_data = {})
        print("Fichier données discord créé")
    
    return data, discord_data

'''
Save data in the json file
Default is set on None if you want save only one file
'''
def save_data(puuidDict = None, discord_data = None):
    
    if puuidDict != None:
        with open(cheminDATA + "data.json", 'w') as file:
                json.dump(puuidDict, file)
    
    if discord_data != None:
        with open(cheminDATA+"discord_data.json", 'w') as file:
            json.dump(discord_data, file)
    
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
    puuidDict, channels = load_data() 
    
    #On remet à jour les données si il y a eu une MAJ de la structure
    if new_MAJ():
        puuidDict, channels = load_data()
    
        

    flag = False #Permet de savoir si une fonction est entrain de parcourir le dictionnaire
    
    
    # When the discord bot is ready
    @bot.event
    async def on_ready():
        check_new_patch.start()
        look_for_last_match.start()
        print(f'Connecté en tant que {bot.user.name}')
    
    async def week_recap():
        print("Envoie du recap de la semaine")
        embed = discord.Embed(
            title="Week recap",
            color=discord.Color.blue()
            )
        for pseudo in puuidDict:
            totalGameWeek = puuidDict[pseudo]['win_week'] + puuidDict[pseudo]['loose_week']
            winRateWeek = round(puuidDict[pseudo]['win_week'] / totalGameWeek * 100)
            value_field = ""
            if puuidDict[pseudo]['win_week'] == 0 and puuidDict[pseudo]['loose_week'] == 0:
                value_field = "No game this week"
            else:
                value_field = f"{puuidDict[pseudo]['win_week']} win {puuidDict[pseudo]['loose_week']} loose - {winRateWeek}% winrate"
                
            embed.add_field(
                name= pseudo,
                value= value_field,
                inline=True
            )
            
        await bot.get_channel(channels['recap']).send(embed=embed)
        puuidDict[pseudo]['win_week'] = 0
        puuidDict[pseudo]['loose_week'] = 0
        save_data(puuidDict)

    schedule_flag = False #Allow to know if the scheduler is already running
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        week_recap,
        trigger="cron",
        day_of_week="sun",
        hour=20,  
        minute=00,
        timezone="Europe/Paris"
    )
    
    @bot.command(name="start_recap")
    async def start_recap(ctx, channel : discord.TextChannel = None):
        nonlocal schedule_flag
        if channel == None and "recap" not in channels.keys():
            await ctx.respond("Please indicate a channel")
        elif schedule_flag:
            await ctx.respond("Recap is already activated")
        else:
            schedule_flag = True
            scheduler.start()
            if channel == None:
                await ctx.respond("The recap will be sent to the channel " + bot.get_channel(channels["recap"]).name)
            else:
                channels["recap"] = channel.id
                save_data(discord_data=channels)
                await ctx.respond("The recap will be sent to the channel : " + channel.name)
    
    @bot.command(name="stop_recap")
    async def stop_recap(ctx):
        if schedule_flag:
            schedule_flag = False
            scheduler.shutdown()
            await ctx.respond("Recap stopped")
        else:
            await ctx.respond("Recap is already stopped")
            
    @bot.command(description="Sends the bot's latency.") 
    async def ping(ctx): 
        await ctx.respond(f"Pong! Latency is : {bot.latency} ms")
    
    @bot.command(description="Stop searching new matchs for all players")
    async def stop_bot(ctx):
        if look_for_last_match.is_running():
            look_for_last_match.stop()
            await ctx.respond("Bot stopped succefully")
        else:
            await ctx.respond("The bot is already stopped")
    
    @bot.command(description="Start searching new match (running by default)")
    async def start_bot(ctx):
        if look_for_last_match.is_running():
            await ctx.respond("The bot is already running")
        else:
            look_for_last_match.start()
            await ctx.respond("The bot is starting")
    
    # Append a player in the dictionnary to watch him
    @bot.command()
    async def add(ctx, pseudo : str, channel : discord.TextChannel):
        flag_add = True
        while flag_add:
            if not(flag):
                flag_add = False
                if pseudo in puuidDict.keys():
                    await ctx.send("Ce pseudo est déjà enregistré")
                else:
                    response = requests.get(f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{pseudo}?api_key={riot}")
                    if response.status_code == 200:
                        response_drMatch = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{response.json()['puuid']}/ids?start=0&count=1&api_key={riot}")
                        
                        if response_drMatch.status_code == 200:
                            response_rang = requests.get(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{response.json()['id']}?api_key={riot}")
                            if response_rang.status_code == 200:
                                puuidDict[pseudo] = crea_dict_player(response_rang.json(), 
                                                                     response.json(), 
                                                                     response_drMatch.json()[0], 
                                                                     channel.id)
                                
                                await ctx.respond(pseudo + " a bien été ajouté")
                            else:
                                await ctx.respond("Erreur lors de la requête du rang : " + str(response_rang.status_code))
                        else:
                            await ctx.respond("Erreur lors de la requête du dernier match : " + str(response.status_code))
                    else:
                        await ctx.respond("Erreur lors de la requête du pseudo : " + str(response.status_code))
                save_data(puuidDict)
            else:
                await asyncio.sleep(0.5)
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
        flag_remove = True #Permet de ne pas enlever un pseudo pendant que l'on parcourt la liste des pseudos
        while flag_remove:
            if not(flag):
                flag_remove = False
                if pseudo in puuidDict.keys():
                    del puuidDict[pseudo]
                    await ctx.respond(pseudo + " a bien été supprimé")
                else:
                    await ctx.respond("Ce pseudo n'est pas enregistré")
                save_data(puuidDict)
            else:
                await asyncio.sleep(0.5)

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
    All 13 seconds, check if the last match of each playcer is same as stored in the dictionnary
    If it's not the same, send a embed message in the discord 
    and update the dictionnary
    '''
    @tasks.loop(seconds=13) 
    async def look_for_last_match():
        flag = True

        for pseudo in puuidDict.keys():
            response = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuidDict[pseudo]['puuid']}/ids?start=0&count=1&api_key={riot}")
            if response.status_code == 200:
                if puuidDict[pseudo]['dernierMatch'] != response.json()[0]: #if the last match is different
                    print(f"Nouveau match trouvé pour {pseudo}")
                    
                    response2 = requests.get(f"https://europe.api.riotgames.com/lol/match/v5/matches/{response.json()[0]}?api_key={riot}")
                    if response2.status_code == 200:
                        response_newRank = requests.get(f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{puuidDict[pseudo]['summonerId']}?api_key={riot}")
                        if response_newRank.status_code == 200:
                            queueId = response2.json()["info"]["queueId"] #const wich define the type of game
                            type_partie = gameType(queueId)
                            win = False
                            remake = response2.json()["info"]["gameDuration"] < 301 #if the game is less than 5 minutes, it's a remake
                            
                            print("Recherche du pseudo dans la game...")
                            for participant in response2.json()["info"]["participants"]:
                                if participant["puuid"] == puuidDict[pseudo]["puuid"]:
                                    win = participant["win"]

                                    print("Verification de la game...")
                                    text_LP = ""
                                    if (queueId == 420 or queueId == 440) and response_newRank.json() != []: #if it's a Solo/Duo or a flex
                                        queueType = "RANKED_SOLO_5x5" if queueId == 420 else "RANKED_FLEX_SR"
                                        
                                        for queue in response_newRank.json():
                                            if queue["queueType"] == queueType:
                                                puuidDict[pseudo], text_LP = update_rank(puuidDict[pseudo], queue, win, queueType)
                                                                            
                                    if win:
                                        puuidDict[pseudo]['win_total'] += 1
                                        puuidDict[pseudo]['win_week'] += 1
                                    else:
                                        puuidDict[pseudo]['loose_total'] += 1
                                        puuidDict[pseudo]['loose_week'] += 1
                                    
                                        
                                    print("Création du message...")
                                    titre = ""
                                    color = discord.Color.green() if win else discord.Color.red()
                                    if remake:
                                        titre = "Remake " + type_partie
                                        color = discord.Color.white()
                                    else:
                                        titre = participant["summonerName"] + " " + ("won" if win else "lost") + " " + type_partie
                                    
                                    embed = discord.Embed(
                                            title=titre,
                                            color=color
                                    )
                                    embed.add_field(
                                        name= participant["championName"] + " - " + str(participant["kills"]) + "/" + str(participant["deaths"]) + "/" + str(participant["assists"]),
                                        value= str(participant["goldEarned"]) + " golds" + text_LP,
                                        inline=True
                                    )
                                    embed.set_thumbnail(
                                        url=f"http://ddragon.leagueoflegends.com/cdn/13.13.1/img/champion/{participant['championName']}.png"
                                    )
                                    embed.timestamp = datetime.datetime.now()
                            
                            print("Création de l'image des perso de la game")
                            gameChampImage = crea_Image(response2.json()["info"]["participants"])
                            print("Sauvegarde en local de l'image...")
                            imsave(chemin+"/others/assembled_image.png", gameChampImage)
                            #I must upload the image to cloudinary to get the url because discord doesn't accept local image
                            print("Upload sur cloudinary de l'image...")
                            cloudinary.uploader.upload(chemin+"/others/assembled_image.png", public_id = "assembled_image", overwrite = True, resource_type = "image")
                            print("Ajout de l'image au message discord...")
                            embed.set_image(url=cloudinary.api.resource("assembled_image")["url"])
                            
                            print("Envoie du message...")
                            await bot.get_channel(puuidDict[pseudo]['channel']).send(embed=embed)
                            print("Message envoyé")
                            
                            print("Mise a jour de la base de données")
                            puuidDict[pseudo]['dernierMatch'] = response.json()[0]
                            save_data(puuidDict)
                            
                        else:
                            print("Erreur lors de la requête du nouveau rank : " + str(response_newRank.status_code))
                            if response_newRank.status_code == 429: #429 : rate lime on attends donc encore un peu
                                await asyncio.sleep(60)
                    else:
                        print("Erreur lors de la requête du dernier match différent : " + str(response2.status_code))
                        if response2.status_code == 429:
                            await asyncio.sleep(60)                       
                else:
                    print("Pas de nouveau match")
            else:
                print("Erreur lors de la requête du dernier match : " + str(response.status_code))
                if response.status_code == 429:
                    await asyncio.sleep(60)        
        flag = False
        
    @tasks.loop(hours=24)
    async def check_new_patch():
        urlChampionsData, urlChamionsImage = new_patch()

    

    bot.run(discord_k)
main()