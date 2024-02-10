import discord  # Pycord
from discord.ext import tasks
from src.configuration import conf
from src.modele.repository import serverRepository
from src.modele.repository import playerRepository
from src.modele.repository import watchRepository
from src.bot import request


def main():
    keys = conf.get_conf_file()
    riot, discord_k, cloudinary_k = keys['riot'], keys['discord'], keys['cloudinary']

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
    async def add(ctx, game_name: str, tag_line: str):
        account_info = await request.get_account(game_name, tag_line)
        if account_info:

            # Check if the player is already in the database
            if not await playerRepository.get_player_by_puuid(account_info['puuid']):
                last_match = await request.get_last_match(account_info['puuid'])
                rank_solo = await request.get_solo_rank(account_info['id'])
                rank_flex = await request.get_flex_rank(account_info['id'])
                await playerRepository.add_player(
                    puuid=account_info['puuid'],
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
                    await ctx.respond(f"{game_name}#{tag_line} is already in the watch list")
                    return

            await watchRepository.add_player_watch(account_info['puuid'], ctx.guild.id)
            await ctx.respond(f"{game_name}#{tag_line} added to the watch list")
        else:
            await ctx.respond("Error")

    @bot.slash_command(description="Remove a player from the watch list")
    async def remove(ctx, game_name: str, tag_line: str):
        account_info = await request.get_account(game_name, tag_line)
        if account_info:
            await watchRepository.delete_player_watch(account_info['puuid'], ctx.guild.id)
            await ctx.respond(f"{game_name}#{tag_line} removed from the watch list")
        else:
            await ctx.respond("Error")

    @tasks.loop(seconds=60)
    async def check_last_match():
        servers = await serverRepository.get_all_servers()
        for server in servers:
            players = await watchRepository.get_players_by_server(server['id_server'])
            for player in players:
                last_match = await request.get_last_match(player['puuid'])
                if last_match != player['dernier_match']:
                    # TODO: changer le dernier match dans la base de données + les win/loose + les ranks
                    await bot.get_channel(server['main_channel']).send(f"{player['pseudo']} has a new match")


    bot.run(discord_k)


main()
