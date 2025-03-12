import discord
from discord.ext import commands, tasks
import statifier as st
import os
from dotenv import load_dotenv

def run_discord_bot():
    load_dotenv(dotenv_path=".env")
    token = os.getenv("DISCORD_TOKEN")

    bot = commands.Bot(command_prefix=",", intents=discord.Intents.default())

    @bot.hybrid_command(name="stats", description="Get my stats")
    async def stats(ctx):
        msg = await ctx.send("fetching stats...")
        statss = await st.get_global_stats()
        await msg.edit(content=f"{ctx.author.mention}\n{statss}")


    @bot.hybrid_command(name="most_played_songs", description="Get my most played")
    async def most_played_songs(ctx: commands.Context, n: int = 5):
        msg = await ctx.send("fetching most played...")
        data = await st.get_most_played(n)
        await msg.edit(content=f"{ctx.author.mention} Your top {n} songs are {data}")

    @bot.hybrid_command(name="most_played_artists", description="Get my most played artists")
    async def most_played_artists(ctx: commands.Context, n: int = 5):
        msg = await ctx.send("fetching most played artists...")
        data = await st.get_most_played_artist(n)
        await msg.edit(content=f"{ctx.author.mention} Your top {n} artists are {data}")

    @bot.hybrid_command(name="get_history_chart", description="Get my history chart")
    async def get_history_chart(ctx: commands.Context, n: int = 7):
        # acknoledge the command
        msg = await ctx.send("fetching history chart...")
        chart = await st.get_history_plot(n)
        file = discord.File(chart, filename="plays_per_day.png")
        await ctx.send(content=f"{ctx.author.mention}", file=file)
        await msg.delete()
        os.remove("plays_per_day.png")

    @bot.event
    async def on_ready():
        await bot.tree.sync()
        print(f'{bot.user} has connected to Discord!')

    bot.run(token)

