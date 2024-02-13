import time

import discord  # Pycord
from discord.ext import tasks
from src.configuration import conf
from src.modele.repository import serverRepository
from src.modele.repository import playerRepository
from src.modele.repository import watchRepository
from src.modele.repository import rankRepository
from src.bot import request
from src.bot import usefulFonctions as util


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

    @bot.slash_command(description="Add a player to the watch list")
    async def add(ctx: discord.Interaction, game_name: str, tag_line: str):
        await ctx.response.defer()
        account_info = await request.get_account(game_name, tag_line)
        if account_info:

            # Check if the player is already in the database
            if not await playerRepository.get_player_by_puuid(account_info['puuid']):
                last_match = await request.get_last_match(account_info['puuid'])
                rank_solo = await request.get_solo_rank(account_info['id'])
                rank_flex = await request.get_flex_rank(account_info['id'])
                await playerRepository.add_player(
                    puuid=account_info['puuid'],
                    game_name_tag_line=game_name + "#" + tag_line,
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
                    await ctx.followup.send(f"{game_name}#{tag_line} is already in the watch list")
                    return

            await watchRepository.add_player_watch(account_info['puuid'], ctx.guild.id)
            await ctx.followup.send(f"{game_name}#{tag_line} added to the watch list")
        else:
            await ctx.followup.send("Error")

    @bot.slash_command(description="Remove a player from the watch list")
    async def remove(ctx: discord.interactions, game_name: str, tag_line: str):
        player = await playerRepository.get_player_by_game_name_tag_line(game_name + "#" + tag_line)
        if player:
            await watchRepository.delete_player_watch(player[0]['puuid'], ctx.guild.id)
            await ctx.respond(f"{game_name}#{tag_line} removed from the watch list")
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
        servers = await serverRepository.get_all_servers()
        for server in servers:
            players = await watchRepository.get_players_by_server(server['id_server'])
            for player in players:
                last_match = await request.get_last_match(player['puuid'])
                if last_match != player['dernier_match']:
                    print(f"{player['pseudo']} has a new match")

                    match = await request.get_last_match_details(last_match)
                    if match:
                        for participant in match['info']['participants']:
                            if participant['puuid'] == player['puuid']:
                                titre = f"{player['pseudo']}"
                                titre += " won " if participant['win'] else " lost "
                                titre += util.game_type(match['info']['queueId'])

                                text_lp = ""
                                text_Arena = ""

                                new_rank = await request.get_rank(match['info']['queueId'], player['sumonerId'])
                                if new_rank:
                                    if match['info']['queueId'] == "RANKED_FLEX_SR":
                                        old_rank = await rankRepository.get_flex_rank(player['puuid'])
                                        await rankRepository.update_flex_rank(player['puuid'], new_rank)
                                    else:
                                        old_rank = await rankRepository.get_solo_rank(player['puuid'])
                                        await rankRepository.update_solo_rank(player['puuid'], new_rank)

                                    text_lp = util.str_rank(old_rank, new_rank, participant['win'])

                                t1 = time.time()
                                image = await util.crea_image(match["info"]["participants"], util.game_type(match['info']['queueId']))
                                print(f"Image créée en {int(time.time() - t1)} secondes")

                                # I don't want hour in my text if the game is less than 1 hour
                                duree_game = ("\nDuree : " +
                                              (time.strftime('%M:%S', time.gmtime(match['info']['gameDuration']))
                                               if match['info']['gameDuration'] <= 3600
                                               else time.strftime('%H:%M:%S', time.gmtime(participant['gameDuration']))))

                                embed = discord.Embed(
                                    title=titre,
                                    description="",
                                    color=discord.Color.green() if participant['win'] else discord.Color.red()
                                )
                                embed.add_field(
                                    name=participant["championName"] + " - " + str(participant["kills"]) + "/" +
                                                str(participant["deaths"]) + "/" + str(participant["assists"]),
                                    value=str(participant["goldEarned"]) + " golds" + text_lp + text_Arena + duree_game,
                                    inline=True
                                )
                                embed.set_thumbnail(
                                    url=util.link_image_champion() + participant['championName'] + ".png"
                                )
                                embed.set_image(url=await util.save_image_cloud(image))
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
                    print(f"{player['pseudo']} has no new match")

    bot.run(discord_k)


main()
