import os
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from yt_dlp import YoutubeDL
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

prefix = '!'

bot = commands.Bot(command_prefix=prefix)
bot.queue = []


# Music bot part!
@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


# Play songs
@bot.command(name='play', help='To play song')
async def play(ctx, *, arg):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    # Context of the current interaction
    bot.voicectx = ctx

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
            length, title, url = info['duration'], info['title'], info['url']
            await ctx.send(f"Now playing {title}. Link: {url}")

            # TODO: -reconnect_delay_max 5 doesn't seem to work on pythonanywhere, why?? (If fixed, also fix it in
            #  the function play_queue
            # FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_delay_max 5', 'options': '-vn'}
            FFMPEG_OPTS = {'before_options': '-reconnect 1', 'options': '-vn'}
            voice.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTS))

        else:
            info['added_by'] = ctx.message.author.name
            bot.queue.append(info)
            await ctx.send(f"Added {info['title']} to the queue!")
    else:
        await join(ctx)
        await play(ctx=ctx, arg=arg)


# Play songs from the queue
async def play_queue(arg, voice):
    length, title, url = arg['duration'], arg['title'], arg['url']

    await bot.voicectx.send(f"Now playing {title}. Link: {url}")

    FFMPEG_OPTS = {'before_options': '-reconnect 1', 'options': '-vn'}
    voice.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTS))


@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await ctx.send("Music is paused.")
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await ctx.send("Music is resumed.")
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use the !play command")


@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='queue', help='Shows the current queue if there is one')
async def queue(ctx):
    # Checking if there is a queue
    if len(bot.queue) > 0:
        # Creating an embed for the queue
        embed = discord.Embed(title="Song queue", description="Songs currently in the queue")

        for i, song in enumerate(bot.queue):
            embed.add_field(name=f"{i + 1}. {song['title']}", value=f"Added by {song['added_by']}", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("queue is empty.")
        return


# Clear the queue
@bot.command(name='clear_queue', help='Clear the queue')
async def clear_queue(ctx):
    bot.queue = []
    await ctx.send("Queue cleared!")


# Remove song from queue
@bot.command(name='remove_from_queue', help='Remove song from queue')
async def remove_from_queue(ctx, *, arg):
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
        if arg <= len(bot.queue):
            # -1 since lists start at 0 while queue starts from 1
            await ctx.send(f"Removed {arg - 1}. {bot.queue[arg - 1]} from the queue")
            bot.queue.pop(arg - 1)
        else:
            await ctx.send("Argument should not be bigger than queue length")


# Check if there is no music playing and if so play the next song in the queue
@tasks.loop(seconds=5.0)
async def check_queue():
    voice = discord.utils.get(bot.voice_clients)

    # Check if bot is in channel
    if voice:
        # Check if bot is playing music
        if not voice.is_playing():
            # Check if queue is nonempty
            if len(bot.queue) > 0:
                arg = bot.queue[0]
                bot.queue.pop(0)
                await play_queue(arg=arg, voice=voice)


check_queue.start()
bot.run(TOKEN)
