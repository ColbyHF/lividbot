import discord
from discord.ext import commands

#
# Basic command that adds the reaction W to a message that includes the word Ratio.
#

class Ratio(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.blacklist = []

    @commands.Cog.listener()
    async def on_message(self, message):
        if "ratio" in message.content.lower() and message.author.id not in self.blacklist:
            await message.add_reaction("🇼")

async def setup(client):
    await client.add_cog(Ratio(client))
