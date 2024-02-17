import time

import discord  # Pycord
from discord.ext import tasks
from src.configuration import conf
from src.modele.repository import serverRepository
from src.modele.repository import playerRepository
from src.modele.repository import watchRepository
from src.modele.repository import rankRepository
from src.bot import request
from src.bot import usefulFonctions as Utils


def main():
    discord_k = conf.get_discord_key()

    bot = discord.Bot()

    @bot.event
    async def on_ready():
        print(f'Connecté en tant que {bot.user.name}')
        id_servers = [guild['id_server'] for guild in await serverRepository.get_all_servers()]
        guilds = bot.guilds

        # Add the servers that are not in the database
        for guild in guilds:
            if guild.id not in id_servers:
                await serverRepository.add_server(guild.id)

        # Delete the servers that are not in the guild's bot anymore
        for id_local_guild in id_servers:
            if id_local_guild not in [guild.id for guild in guilds]:
                await serverRepository.delete_server(id_local_guild)
        print("Update server list : done")
        check_last_match.start()
        print("Check last match : started")

    @bot.event
    async def on_guild_remove(guild):
        print(f"Bot removed from {guild.name}")
        await serverRepository.delete_server(guild.id)

    @bot.event
    async def on_guild_join(guild):
        print(f"Bot joined {guild.name}")
        await serverRepository.add_server(guild.id)

    @bot.slash_command(description="Set the channel where the bot will send all the messages")
    async def set_main_channel(ctx, channel: discord.TextChannel):
        await serverRepository.update_server(ctx.guild.id, main_channel=channel.id)
        await ctx.respond(f"Main channel set to {channel.name}")

    async def autocomplete_remove_add(ctx: discord.AutocompleteContext):
        players = await playerRepository.get_all_players_watch()
        return [player["gameName_tagLine"] for player in players]

    @bot.slash_command(description="Add a player to the watch list")
    async def add(
            ctx: discord.Interaction,
            player: discord.Option(
                str,
                "Format : example#1234",
                autocomplete=discord.utils.basic_autocomplete(autocomplete_remove_add),
                )
    ):
        await ctx.response.defer()
        if not ('#' in player):
            await ctx.followup.send("Error : the player must be in the format 'game_name#tag_line'")
            return

        account_info = await request.get_account(player)
        if account_info:

            # Check if the player is already in the database
            if not await playerRepository.get_player_by_puuid(account_info['puuid']):
                last_match = await request.get_last_match(account_info['puuid'])
                rank_solo = await request.get_solo_rank(account_info['id'])
                rank_flex = await request.get_flex_rank(account_info['id'])
                await playerRepository.add_player(
                    puuid=account_info['puuid'],
                    game_name_tag_line=player,
                    sumonerId=account_info['id'],
                    pseudo=account_info['name'],
                    dernier_match=last_match,
                    loose_week=0,
                    win_week=0,
                    rank_flex=rank_flex,
                    rank_solo=rank_solo
                )
            else:
                # Check if the player is already in the watch list of the server
                if await watchRepository.player_watch(account_info['puuid'], ctx.guild.id):
                    await ctx.followup.send(f"{player} is already in the watch list")
                    return

            await watchRepository.add_player_watch(account_info['puuid'], ctx.guild.id)
            await ctx.followup.send(f"{player} added to the watch list")
        else:
            await ctx.followup.send("Error")

    @bot.slash_command(description="Remove a player from the watch list")
    async def remove(
            ctx: discord.interactions,
            pseudo: discord.Option(
                str,
                "Format : example#1234",
                autocomplete=discord.utils.basic_autocomplete(autocomplete_remove_add))):
        player = await playerRepository.get_player_by_game_name_tag_line(pseudo)
        if player:
            await watchRepository.delete_player_watch(player[0]['puuid'], ctx.guild.id)
            await ctx.respond(f"{player} removed from the watch list")
        else:
            await ctx.respond("Player not found")

    @bot.slash_command(description="Show the watch list")
    async def watch_list(ctx):
        players = await watchRepository.get_players_by_server(ctx.guild.id)
        if players:
            players = "\n".join([f"{player['pseudo']} - {player['gameName_tagLine']}" for player in players])
            await ctx.respond(players)
        else:
            await ctx.respond("No player in the watch list")

    @tasks.loop(seconds=30)
    async def check_last_match():
        players = await playerRepository.get_all_players_watch()
        for player in players:
            last_match = await request.get_last_match(player['puuid'])
            if last_match != player['dernier_match'] and last_match != "":
                print(f"{player['pseudo']} has a new match")

                match = await request.get_last_match_details(last_match)
                if match:
                    for participant in match['info']['participants']:
                        if participant['puuid'] == player['puuid']:
                            titre = f"{player['pseudo']}"
                            titre += " won " if participant['win'] else " lost "
                            titre += Utils.game_type(match['info']['queueId'])

                            text_lp = ""
                            text_Arena = ""

                            new_rank = await request.get_rank(match['info']['queueId'], player['sumonerId'])
                            if new_rank:
                                if match['info']['queueId'] == 440:
                                    old_rank = await rankRepository.get_flex_rank(player['puuid'])
                                    await rankRepository.update_flex_rank(player['puuid'], new_rank)
                                else:
                                    old_rank = await rankRepository.get_solo_rank(player['puuid'])
                                    await rankRepository.update_solo_rank(player['puuid'], new_rank)

                                text_lp = Utils.str_rank(old_rank, new_rank, participant['win'])

                            print("Création de l'image...")
                            t1 = time.time()
                            image = await Utils.crea_image(match["info"]["participants"],
                                                          Utils.game_type(match['info']['queueId']))
                            print(f"Image créée en {int(time.time() - t1)} secondes")

                            # I don't want hour in my text if the game is less than 1 hour
                            duree_game = ("\nDuration : " +
                                          (time.strftime('%M:%S', time.gmtime(match['info']['gameDuration'])) + " min"
                                           if match['info']['gameDuration'] <= 3600
                                           else time.strftime('%H:%M:%S', time.gmtime(participant['gameDuration']))))

                            text_gold_damage_cs = (f"{participant['goldEarned']} golds - "
                                                   f"{participant['totalDamageDealtToChampions']} damages - "
                                                   f"{participant['totalMinionsKilled'] + participant['neutralMinionsKilled']} cs")
                            embed = discord.Embed(
                                title=titre,
                                description="",
                                color=discord.Color.green() if participant['win'] else discord.Color.red()
                            )
                            embed.add_field(
                                name=participant["championName"] + " - " + str(participant["kills"]) + "/" +
                                     str(participant["deaths"]) + "/" + str(participant["assists"]),
                                value=text_gold_damage_cs + text_lp + text_Arena + duree_game,
                                inline=True
                            )
                            embed.set_thumbnail(
                                url=Utils.link_image_champion() + participant['championName'] + ".png"
                            )
                            embed.set_image(url=await Utils.save_image_cloud(image))

                            id_servers = await watchRepository.get_server_by_player(player['puuid'])

                            for id_server in id_servers:
                                server = await serverRepository.get_server(id_server['id_server'])
                                if server['main_channel']:
                                    await (bot.get_guild(server['id_server']).get_channel(server['main_channel'])
                                           .send(embed=embed))
                                else:
                                    await (bot.get_guild(server['id_server']).text_channels[0].send(
                                        "Use /set_main_channel to set a channel where the bot will send"
                                        " all the messages",
                                        embed=embed))

                            await playerRepository.update_player_last_match(player['puuid'], last_match)
                else:
                    print("Error : player not found in the game")
            else:
                # print(f"{player['pseudo']} has no new match")
                pass

    bot.run(discord_k)


main()
