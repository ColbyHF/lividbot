import discord
from discord.ext import commands

#
# Simple ping pong command.
#


class Pings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping.py Is Ready.")

    @commands.command()
    async def ping(self, ctx):
        bot_latency = round(self.client.latency * 1000)

        await ctx.send(f"{bot_latency} ms.")

async def setup(client):
    await client.add_cog(Pings(client))
