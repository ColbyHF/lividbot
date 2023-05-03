import discord
from discord.ext import commands


#
# Basic Purge command, little messed up when inputing a number of messages to delete outside of that everything works.
#



class Purge(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='purge', help='Purges a specified number of messages from the channel')
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, num_messages: int = None):
        if num_messages is None:
            await ctx.send('Please specify the number of messages to purge.')
            return
        await ctx.channel.purge(limit=num_messages + 1)
        await ctx.send(f'{num_messages} messages have been purged.', delete_after=5)

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Please enter a valid number of messages to purge.')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to purge messages.")
        else:
            await ctx.send('An error occurred while purging messages.')

async def setup(client):
    await client.add_cog(Purge(client))
