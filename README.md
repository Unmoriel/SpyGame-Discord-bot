# SpyGame-Discord-bot - EN

The principle of the bot is simple:

You add it to the server, you add yourself to the bot's list using the */add 'your_lol_username'* command.

Then, whenever you finish a game, it sends a message to a channel summarizing your game.

You can view the list of people the bot follows using the */list* command and remove someone using the */remove 'your_lol_username'* command.

I provide only the code and explain how to set it up, but you must host the bot yourself.

I also assume that you already know how to set up a Discord bot, otherwise everything is well explained by Discord itself.

*******

Python libraries required:
* discord
* os
* cloudinary
* matplotlib.image
* numpy
* requests
* json
* datetime

*******

Required APIs:
* Riot Games
* Discord
* cloudinary

*******

To set up the bot, here is the file structure you should have:

*botFile*<br>
-> *SpyBot*<br>
-> -> main.py<br>
-> data<br>
-> -> champion<br>
-> -> -> ...<br>
-> -> other<br>
-> -> temp<br>
-> -> apiKey.json<br>

The names of the non-italicized folders/files should not be changed.
main.py is the bot's file, which is located in this git repository.
In the data folder:
The champions folder is located in the compressed file that you can find at this link:
https://developer.riotgames.com/docs/lol#data-dragon
others is the folder located in the git repository (it contains useful images)
temp is a folder that will contain temporary files for the bot (it is empty by default)
apikey.json is a JSON file that contains the necessary API keys. It is structured as follows:
{ <br>
"discord": "key", <br>
"riot":"key",<br>
"cloudinary" : {<br>
"cloud_name" : "name_cloud",<br>
"api_key" : "key",<br>
"api_secret" :"key"<br>
}<br>
}<br>

As for how the bot works, I leave it to you to look at the code, as it is usually sufficiently commented.

Command :

* /add username: (adds your username to the list of players for which the bot monitors the history)
* /remove username: (removes your username from this list)
* /list: returns the list of all usernames that the bot monitors the history for
* /here: command to be executed in the text channel where you want the bot to send win or loss messages (by default, the bot uses the first text channel of your server).

username is your League of Legend username do not confuse it with your riot id

********************
# SpyGame-Discord-bot - FR

Le principe du bot est simple :

Vous l'ajoutez au serveur, vous ajoutez dans la liste du bot grâce à la commande */add 'votre_pseudo_lol'*. 

Ensuite, dès que vous terminez une partie, il envoie un message dans un canal en résumant votre partie. 

Vous pouvez voir la liste des personnes que le bot suit grâce à la commande */liste* et supprimer quelqu'un grâce à la commande */remove 'votre_pseudo_lol'*.

Je fournis uniquement le code et vous explique comment le mettre en place, mais vous devez héberger vous-même le bot.

Je pars aussi du principe que vous savez déjà comment mettre en place un bot Discord, sinon tout est très bien expliqué par Discord lui-même.

*******

Librairies Python dont vous avez besoin :
* discord
* os
* cloudinary (necessaire car discord n'accepte que les images qui sont stocké sur internet)
* matplotlib.image
* numpy
* requests
* json
* datetime

*******

API nécessaires :
* Riot Games
* Discord
* cloudinary

*******

Pour mettre en place le bot, voici l'arborescence de fichiers que vous devez avoir :

*botFile*<br>
-> *SpyBot*<br>
-> -> main.py<br>
-> data<br>
-> -> champion<br>
-> -> -> ...<br>
-> -> other<br>
-> -> temp<br>
-> -> apiKey.json<br>

Les noms des dossiers/fichiers qui ne sont pas en italiques ne doivent pas être changés.
main.py est le fichier du bot, qui se trouve dans ce répertoire git.
Dans le dossier data :
Le dossier champions se trouve dans le fichier compressé que vous pouvez trouver à ce lien :
https://developer.riotgames.com/docs/lol#data-dragon
others est le dossier qui se trouve dans le répertoire git (il contient des images utiles)
temp est un dossier qui contiendra des fichiers temporaires pour le bot (il est vide de base)
apikey.json est un fichier JSON qui contient les clés des API nécessaires. Il se construit de la manière suivante :
{ <br>
"discord": "key", <br>
"riot":"key",<br>
"cloudinary" : {<br>
"cloud_name" : "name_cloud",<br>
"api_key" : "key",<br>
"api_secret" :"key"<br>
}<br>
}<br>

Pour ce qui est du fonctionnement du bot, je vous laisse le soin de regarder le code, il est normalement suffisamment commenté.

Commandes :

* /add pseudo : (ajoute ton pseudo à la liste des joueurs pour lesquels le bot surveille l'historique)
* /remove pseudo : (enlève ton pseudo de cette liste)
* /list : renvoie la liste de tous les pseudos dont le bot surveille l'historique
* /here : commande à exécuter dans le salon textuel où tu veux que le bot envoie les messages de victoire ou de défaite (par défaut, le bot utilise le premier canal textuel de ton serveur).

pseudo corresond à votre pseudo League of Legend (et pas forcement votre riot id)
