import discord
from discord.ext import commands

#
# This takes the mentioned users avatar and enlarges it.
#



class Avatar(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Avatar.py Is Ready.")

    @commands.command()
    async def avatar(self, ctx, *, member: discord.Member,):
        try:
            if member == None:
                member = ctx.author

            embed = discord.Embed(title=f"{member.display_name}'s Avatar", color=member.color)
            embed.set_image(url=member.avatar)

            await ctx.send(embed=embed)
        except Exception as e:
            print(e)

async def setup(client):
    await client.add_cog(Avatar(client))
