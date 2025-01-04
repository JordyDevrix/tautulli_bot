import discord
from discord.ext import commands, tasks
import statifier as st
import os


def run_discord_bot():
    os.getenv("DISCORD_TOKEN")
    token = os.getenv("DISCORD_TOKEN")
    print(token)

    bot = commands.Bot(command_prefix=",", intents=discord.Intents.default())

    @bot.hybrid_command(name="stats", description="Get my stats")
    async def stats(ctx):
        await ctx.send(st.get_global_stats())

    @bot.hybrid_command(name="most_played_songs", description="Get my most played")
    async def most_played_songs(ctx: commands.Context, n: int = 5):
        msg = await ctx.send("fetching most played...")
        data = st.get_most_played(n)
        await msg.edit(content=f"{ctx.author.mention} Your top {n} songs are {data}")

    @bot.hybrid_command(name="most_played_artists", description="Get my most played artists")
    async def most_played_artists(ctx: commands.Context, n: int = 5):
        msg = await ctx.send("fetching most played artists...")
        data = st.get_most_played_artist(n)
        await msg.edit(content=f"{ctx.author.mention} Your top {n} artists are {data}")

    @bot.hybrid_command(name="get_history_chart", description="Get my history chart")
    async def get_history_chart(ctx: commands.Context, n: int = 7):
        msg = await ctx.send("Generating chart...")
        file = st.get_history_plot(n)
        await msg.channel.send(file=discord.File(file))
        await msg.delete()
        os.remove(file)

    @bot.event
    async def on_ready():
        await bot.tree.sync()
        print(f'{bot.user} has connected to Discord!')

    bot.run(token)

