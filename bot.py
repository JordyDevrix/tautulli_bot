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

    @bot.hybrid_command(name="most_played", description="Get my most played")
    async def most_played(ctx: commands.Context, n: int = 5):
        msg = await ctx.send("fetching most played...")
        data = st.get_most_played(n)
        await msg.edit(content=f"{ctx.author.mention} Your top 10 songs are {data}")

    @bot.event
    async def on_ready():
        await bot.tree.sync()
        print(f'{bot.user} has connected to Discord!')

    bot.run(token)

