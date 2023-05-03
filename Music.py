import discord
from discord.ext import commands
import logging
import asyncio
import yt_dlp
import youtube_dl

logging.basicConfig(level=logging.INFO)

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.song_queue = []
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
        if len(self.song_queue) > 0:
            song = self.song_queue.pop(0)
            logging.info(f"Playing song: {song['title']}")
            ctx.voice_client.play(discord.FFmpegPCMAudio(song['url'], **self.FFMPEG_OPTIONS))
            await asyncio.sleep(1)
            await ctx.send(f'Now playing: {song["title"]}')
        else:
            await ctx.send("The queue is empty.")

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

                self.song_queue.append({'title': title, 'url': url})

                if not ctx.voice_client.is_playing():
                    await self.play_next_song(ctx)
                else:
                    await ctx.send(f'Added to queue: {title}')
            except Exception as e:
                logging.error(e)
                await ctx.send("Sorry, I could not play that song. Please check the URL or try another song.")

    @commands.command(aliases=['sk', 's'], help='Skips the current song')
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await self.play_next_song(ctx)
        else:
            await ctx.send("I am not playing any music.")

    @commands.command(aliases=['queue', 'q'], help='Shows the current queue')
    async def show_queue(self, ctx):
        if not self.song_queue:
            return await ctx.send('The queue is currently empty.')

        queue_list = ''
        for i, song in enumerate(self.song_queue, 1):
            queue_list += f'{i}. {song["title"]}\n'

        await ctx.send(f'Current queue:\n{queue_list}')

    @commands.command(aliases=['next', 'n'], help='Plays the next song in queue')
    async def next_song(self, ctx):
        if len(self.song_queue) > 0:
            url = self.song_queue[0]['url']
            title = self.song_queue[0]['title']
            del self.song_queue[0]
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

                self.song_queue.append({'title': title, 'url': url})
                logging.info(f"Added song to queue: {title}")
                await ctx.send(f'Added to queue: {title}')
            except Exception as e:
                logging.error(e)
                await ctx.send("Sorry, I could not add that song. Please check the URL or try another song.")

    @commands.command(aliases=['die', 'dc', 'disconnect'], help='Stops playing and clears the queue')
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.song_queue.clear()
        else:
            await ctx.send("I am not connected to a voice channel.")
            await ctx.send("I've disconnected from the voice channel.")

async def setup(client):
     await client.add_cog(Music(client))
