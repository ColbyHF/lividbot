import discord
from discord.ext import commands

#
# This snipes the last message that was deleted.
#



class Snipe(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.sniped_messages = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.sniped_messages[message.channel.id] = message

    @commands.command()
    async def snipe(self, ctx):
        if ctx.channel.id in self.sniped_messages:
            message = self.sniped_messages[ctx.channel.id]
            embed = discord.Embed(title="Sniped Yo Ass")
            embed.set_author(name=message.author.display_name)
            embed.add_field(name="Message Content", value=message.content, inline=False)
            embed.set_footer(text=f"Deleted in #{message.channel}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("No recently deleted messages in this channel.")

async def setup(client):
    await client.add_cog(Snipe(client))
    
