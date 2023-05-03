import discord
from discord.ext import commands


#
# This command snipes the last message that was edited.
#




class Snipee(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.last_edited_message = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Snipee.py Is Ready.")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        self.last_edited_message[before.channel] = (before.content, after.content)

    @commands.command()
    async def snipee(self, ctx):
        if ctx.channel not in self.last_edited_message:
            await ctx.send("There's nothing to snipe!")
            return

        before, after = self.last_edited_message[ctx.channel]
        embed = discord.Embed(title="Last Edited Message", color=discord.Color.blue())
        embed.add_field(name="Before", value=before or "Empty", inline=False)
        embed.add_field(name="After", value=after or "Empty", inline=False)
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Snipee(client))
