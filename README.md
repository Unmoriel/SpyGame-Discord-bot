# SpyGame-Discord-bot

Le principe du bot est simple : <br>
Vous l'ajoutez au serveur, vous ajoutez dans la liste du bot grace au */add 'votre_pseudo_lol'*. <br>
Ensuite dès que vous terminez une partie, il envois un message dans un canal en résumant votre partie. <br>
Vous pouvez voir la liste des personnes que le bot suit grace à la commande */liste* et supprimer quelqu'un grace a */remove 'votre_pseudo_lol'*. <br>

Je fournis uniquement le code et vous explique comment le mettre en place mais vous devez hebergez vous même le bot.<br>
Je pars aussi du principe que vous savez déjà comment mettre en place un bot discord, sinon tout est très bien expliqué par discord lui même. <br>

*******
Librairies python dont vous avez besoins : 
* discord 
* os
* cloudinary
* cv2 (OpenCV)
* numpy
* requests
* json
* datetime
*******
API nécéssaire :
* Riot Games
* Dicord
* cloudinary
*******
Pour mettre en place le bot voici l'arborescence de fichier que vous devez avoir :

*botFile* <br>
->*SpyBot* <br>
->->main.py <br
->data <br>
->->champion <br>
->->->... <br>
->->other <br>
->->temp <br>
->->apiKey.json <br>

Les noms des dossiers/fichier qui ne sont pas en italiques ne doivent pas être changé. <br>
main.py est le fichier du bot, qui se trouve dans ce repertoire git. <br>
Dans le dossier data : <br>
Le dossier champions se trouve dans le fichier compressé que vous pouvez trouver à ce lien : <br>
https://developer.riotgames.com/docs/lol#data-dragon <br>
others est le dossier qui se trouve dans le repertoire git (il contient des images utiles) <br>
temp est un dossier qui contiendra des fichiers temporaires pour le bot (il est vide de base) <br>
apikey.json est un fichier json qui contient les clées des apis nécéssaires. Il se construit de la manière suivante : <br>
{ <br>
"discord": "key", <br>
"riot":"key", <br>
"cloudinary" : { <br>
    "cloud_name" : "name_cloud", <br>
    "api_key" : "key", <br>
    "api_secret" :"key" <br>
    } <br>
} <br>

Pour ce qui est du fonctionnement du bot je vous laisse le soin de regarder le code, il est normalement suffisemment commenté.






