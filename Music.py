import discord
from discord.ext import commands
import logging
import asyncio
import yt_dlp

logging.basicConfig(level=logging.INFO)

#
# Basic music bot. Functions properly and works
#

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queue = []
        self.is_first_song = True
        self.is_playing = False
        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        self.FFMPEG_OPTIONS = {
            'options': '-vn',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        }

    async def play_next_song(self, ctx):
        if not self.queue:
            self.is_playing = False
            return

        # check if a song is already playing
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        song = self.queue.pop(0)
        self.current_song = song

        ctx.voice_client.play(
            discord.FFmpegPCMAudio(song['url'], **self.FFMPEG_OPTIONS),
            after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.client.loop).result()
        )
        await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
        embed = discord.Embed(title="Now Playing", description=song["title"], color=0x00ff00)
        await ctx.send(embed=embed)

    @commands.command(aliases=['j', 'jo'], help='Joins the voice channel')
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("You are not connected to a voice channel.")
            return
        voice_channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

        await ctx.send("I've joined the voice channel.")
        await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)

    @commands.command(aliases=['pl', 'p'], help='Plays a song')
    async def play(self, ctx, *, searchword):
        async with ctx.typing():
            # check if user is in a voice channel, and join the channel if not
            if not ctx.author.voice:
                return await ctx.send("You are not connected to a voice channel.")
            voice_channel = ctx.author.voice.channel
            if not ctx.voice_client:
                await voice_channel.connect()
                await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
            else:
                await ctx.voice_client.move_to(voice_channel)

            try:
                if searchword[0:4] != "http" and searchword[0:3] != "www":
                    with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(f"ytsearch:{searchword}", download=False)["entries"][0]
                        title = info["title"]
                        url = info["url"]
                else:
                    url = searchword
                    with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(url, download=False)
                        title = info['title']

                if ctx.voice_client.is_playing() or self.is_playing:
                    self.queue.append({'title': title, 'url': url})
                    embed = discord.Embed(title="Added to Queue", description=title, color=0xff0000)
                    await ctx.send(embed=embed)
                else:
                    self.is_playing = True
                    ctx.voice_client.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.client.loop).result())
                    embed = discord.Embed(title="Now Playing", description=title, color=0x00ff00)
                    await ctx.send(embed=embed)

                    # Remove the current song from the queue after it's finished playing
                    def after_playing(error):
                      self.is_playing = False
                      asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.client.loop).result()
                    
                    ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
                    ctx.voice_client.source.volume = 1
                    ctx.voice_client.source.after = after_playing

            except Exception as e:
                    logging.error(e)
                    await ctx.send("Sorry, I could not play that song. Please check the URL or try another song.")

    @commands.command(aliases=['s','sk'], help='Skips the current song')
    async def skip(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client or not voice_client.is_playing():
            await ctx.send("I am not currently playing any song.")
            return
        voice_client.stop()
        await voice_client.on_track_end.wait()  # wait for the current song to end
        await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
        await self.play_next_song(ctx)
        await ctx.send("Skipped the current song!")

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        if not self.queue:
            await ctx.send("There are no songs in the queue.")
            return

        queue_list = '\n'.join([f"{i + 1}. {song['title']}" for i, song in enumerate(self.queue)])

        embed = discord.Embed(title="Queue", description=queue_list, color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(aliases=['next', 'n'], help='Plays the next song in queue')
    async def next_song(self, ctx):
        if len(self.queue) > 0:
            url = self.queue[0]['url']
            title = self.queue[0]['title']
            del self.queue[0]
            ctx.voice_client.play(discord.FFmpegPCMAudio(url, **self.FFMPEG_OPTIONS))
            await asyncio.sleep(3)
            await ctx.send(f'Now playing: {title}')
        else:
            await ctx.send('The queue is currently empty.')

    @commands.command(aliases=['add', 'a'], help='Adds a song to the queue')
    async def add_song(self, ctx, *, searchword):
        async with ctx.typing():
            try:
                if searchword[0:4] != "http" and searchword[0:3] != "www":
                    with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(f"ytsearch:{searchword}", download=False)["entries"][0]
                        title = info["title"]
                        url = info["url"]
                else:
                    url = searchword
                    with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(url, download=False)
                        title = info['title']

                self.queue.append({'title': title, 'url': url})
                logging.info(f"Added song to queue: {title}")
                await ctx.send(f'Added to queue: {title}')
            except Exception as e:
                logging.error(e)
                await ctx.send("Sorry, I could not add that song. Please check the URL or try another song.")

    @commands.command(aliases=['die', 'dc', 'disconnect'], help='Stops playing and clears the queue')
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queue.clear()
        else:
            await ctx.send("I am not connected to a voice channel.")
            await ctx.send("I've disconnected from the voice channel.")

async def setup(client):
     await client.add_cog(Music(client))
