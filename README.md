<h1>!This readme is currently being rewritten, so only the French version is correct at the moment.!</h1>

# SpyGame-Discord-bot - EN

The principle of the bot is simple:

You add it to the server, you add yourself to the bot's list using the */add 'your_lol_username'* command.

Then, whenever you finish a game, it sends a message to a channel summarizing your game.

You can view the list of people the bot follows using the */list* command and remove someone using the */remove 'your_lol_username'* command.

I provide only the code and explain how to set it up, but you must host the bot yourself.

I also assume that you already know how to set up a Discord bot, otherwise everything is well explained by Discord themself.

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
<h1> SpyGame-Discord-bot - FR</h1>

<h4>Résumé :</h4>
<p>
Ce bot permet de voir le résultat des parties de LoL de n'importe qui tant que vous avez son pseudo. À chaque fin de game le bot envoie un message contenant un résumé de la partie
<p>

<h4>Précisions :</h4>
<p>
Je ne suis pas un développeur pro.
<br>
Je vous fournit un code qui vous permet de faire fonctionner un bot discord. Je ne vous explique pas comment en créer un.
<br>
Le bot et la base de données ne sont pas destinés à suivre une grande quantité de joueur. Le bot peut supporter de base une dizaine de personnes, mais vous pouvez augmenter jusqu'à 20 - 25 si vous optimisez le code.
<br>
Enfin, le plus grand inconvénient du bot est la nécessité d'obtenir une clé API "personal" ou "production". La clé "personal" est celle que je recommande. Elle ne débloque pas le plafond de requêtes maximums mais c'est la plus simple à avoir. Personnellement, je l'ai obtenu en un peu moins de deux semaines en mettant ce projet Github en lien.
</p>

<h3>Librairies pythons nécessaires :</h3>

* Python 3.11
* discord
* os
* cloudinary 
* matplotlib.image
* numpy
* requests
* json
* datetime

<h3>API nécessaires :</h3>

* Riot Games
* Discord
* cloudinary


<h2>Préparation</h2>

<p>Pour l'API de Riot Game, vous allez devoir demander une clé produit ou personnel sur leur site : <a>https://developer.riotgames.com/</a> </p>

<p>Pour l'API de discord, vous devez mettre en place un bot. C'est expliqué par exemple ans la documentation de Pycord : <a>https://guide.pycord.dev/introduction</a></p>

<p>Enfin, j'utilise cloudinary pour stocker des images sur Internet. Cela me permet de pouvoir les mettre dans les messages "embed" de Discord. Il suffit de créer un compte gratuit : <a>https://cloudinary.com/</a> </p>

<h2>Installation</h2>

<p>Clonez le dépôt Github et remplissez le fichier 'apiKeys.json' qui se trouve dans le dossier data.
Il se construit de la manière suivante : <br>
{ <br>
"discord": "key", <br>
"riot":"key",<br>
"cloudinary" : {<br>
"cloud_name" : "name_cloud",<br>
"api_key" : "key",<br>
"api_secret" :"key"<br>
}<br>
}<br>

Il vous faut remplacer les 'key' par les clés d'API correspondante (Discord appelle cela un Token). Attention, les clés d'API sont des données sensibles.
</p>

<h2>Lancement</h2>
<p>Exécutez avec python le fichier main.py. Le bot doit s'afficher comme connecté. Les commandes peuvent mettre un peu de temps à apparaître.</p>

<p>Pour ce qui est du fonctionnement du bot, je vous laisse le soin de regarder le code dans main.py. J'ai commenté les fonctions principales en anglais, mais les commentaires plus précis sont en français (désolé).</p>

<h2>Commandes :</h2>

<ul>
    <li><b>/add</b> "pseudo" "channel" <br>Vous ajoute à la base de données du bot. C'est-à-dire que dès que vous ferez une game, le résultat sera envoyer dans le channel discord que vous avez entrer.</li>
    <li><b>/remove</b> "pseudo"<br>Supprime votre pseudo de la base de données (et toutes les informations qui vont avec elle). Une auto-complétion sur tous les pseudo de base de données est disponible. </li>
    <li><b>/list</b><br>Affiche la liste des pseudo enregistrés dans la base de données.</li>
    <li><b>/ping</b><br>Affiche la latence du bot.</li>
</ul>

<p>"pseudo" correspond à votre nom d'invocateur en jeu. Pas forcément à votre Riot ID qui peut-être différent.</p>