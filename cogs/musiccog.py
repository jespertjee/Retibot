from discord.ext import tasks, commands
from yt_dlp import YoutubeDL
import discord
import requests


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []

    @commands.command(name='join', help='Tells the bot to join the voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
            return
        else:
            channel = ctx.message.author.voice.channel
        await channel.connect()

    @commands.command(name='leave', help='Bot leave the voice channel')
    async def leave(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
        else:
            await ctx.send("The bot is not connected to a voice channel.")

    # Play songs
    @commands.command(name='play', help='To play song')
    async def play(self, ctx, *, arg):
        if not ctx.message.author.voice:
            ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
            return
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        # Context of the current interaction
        self.bot.voicectx = ctx

        if voice:
            # Getting the info about the search query
            with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as ydl:
                try:
                    requests.get(arg)
                except:
                    info = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
                else:
                    info = ydl.extract_info(arg, download=False)


            if not voice.is_playing():
                length, title, url = info['duration'], info['title'], info['webpage_url']
                await ctx.send(f"Now playing {title}. Link: {url}")

                # TODO: -reconnect_delay_max 5 doesn't seem to work on pythonanywhere, why?? (If fixed, also fix it in
                #  the function play_queue
                # FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_delay_max 5', 'options': '-vn'}
                FFMPEG_OPTS = {'before_options': '-reconnect 1', 'options': '-vn'}
                voice.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTS))

            else:
                info['added_by'] = ctx.message.author.name
                self.queue.append(info)
                await ctx.send(f"Added {info['title']} to the queue!")
        else:
            await self.join(ctx)
            await self.play(ctx=ctx, arg=arg)

    # Play songs from the queue
    async def play_queue(self, arg, voice):
        length, title, url = arg['duration'], arg['title'], arg['url']

        await self.bot.voicectx.send(f"Now playing {title}. Link: {url}")

        FFMPEG_OPTS = {'before_options': '-reconnect 1', 'options': '-vn'}
        voice.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTS))

    @commands.command(name='pause', help='Pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await ctx.send("Music is paused.")
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await ctx.send("Music is resumed.")
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use the !play command")

    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything at the moment.")

    @commands.command(name='queue', help='Shows the current queue if there is one')
    async def queue(self, ctx):
        # Checking if there is a queue
        if len(self.queue) > 0:
            # Creating an embed for the queue
            embed = discord.Embed(title="Song queue", description="Songs currently in the queue")

            for i, song in enumerate(self.queue):
                embed.add_field(name=f"{i + 1}. {song['title']}", value=f"Added by {song['added_by']}", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("queue is empty.")
            return

    # Clear the queue
    @commands.command(name='clear_queue', help='Clears the queue')
    async def clear_queue(self, ctx):
        self.queue = []
        await ctx.send("Queue cleared!")

    # Remove song from queue
    @commands.command(name='remove_from_queue', help='Removes song from queue')
    async def remove_from_queue(self, ctx, *, arg):
        # See if arg is actually an integer
        try:
            arg = int(arg)
        except ValueError:
            await ctx.send("Argument should be an integer")
        if isinstance(arg, int):
            # Argument can't be 0
            if arg == 0:
                await ctx.send("Argument should not be 0")
            if arg < 0:
                await ctx.send("Argument should not be negative")

            # Argument can't be bigger than queue length
            if arg <= len(self.queue):
                # -1 since lists start at 0 while queue starts from 1
                await ctx.send(f"Removed {arg - 1}. {self.queue[arg - 1]} from the queue")
                self.queue.pop(arg - 1)
            else:
                await ctx.send("Argument should not be bigger than queue length")

    # Check if there is no music playing and if so play the next song in the queue
    @tasks.loop(seconds=5.0)
    async def check_queue(self):
        voice = discord.utils.get(self.bot.voice_clients)

        # Check if bot is in channel
        if voice:
            # Check if bot is playing music
            if not voice.is_playing():
                # Check if queue is nonempty
                if len(self.queue) > 0:
                    arg = self.queue[0]
                    self.queue.pop(0)
                    await self.play_queue(arg=arg, voice=voice)


def setup(bot):
    bot.add_cog(MusicCog(bot))