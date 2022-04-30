import os

import pandas as pd
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from yt_dlp import YoutubeDL
import requests
import numpy as np
import data_analysis

# import logging
#
# # Logging settings
# logger = logging.getLogger(__name__)
#
# # Setting up the handler
# f_handler = logging.FileHandler('info.log')
# f_handler.setLevel(logging.INFO)
#
# # Setting up the formatter
# f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# f_handler.setFormatter(f_format)
#
# logger.addHandler(f_handler)

# Generic bot settings
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


@bot.command(name='leave', help='Bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


# Play songs
@bot.command(name='play', help='To play song')
async def play(ctx, *, arg):
    if not ctx.message.author.voice:
        ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
        return
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


@bot.command(name='pause', help='Pauses the song')
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
@bot.command(name='clear_queue', help='Clears the queue')
async def clear_queue(ctx):
    bot.queue = []
    await ctx.send("Queue cleared!")


# Remove song from queue
@bot.command(name='remove_from_queue', help='Removes song from queue')
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

# TODO: tons of edge cases I havent added errors for here, should do that
@bot.command(name='define', help='Define a word using google dictionary')
async def define(ctx, * arg):
    # Creating the query from the argument
    query = ""
    print_query = ""
    for word in arg:
        query += word
        query += "%20"
        print_query += word
        print_query += " "
    # Removing the last empty space/%20 from both
    print_query = print_query[0:-1]
    query = query[0:-3]


    # Getting the data from https://dictionaryapi.dev/
    try:
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{query}")
        r.raise_for_status()
    # TODO: make this not a generic except
    except:
        await ctx.send(f"An error has occurred, are you sure that is a proper search query?")
        return

    data = r.json()[0]

    # Seeing if there is a definition, if so post it
    if data['meanings']:
        meanings = data['meanings'][0]
        if meanings['definitions']:
            definition = meanings['definitions'][0]

            await ctx.send(f"**{print_query}**: {definition['definition']}")


@bot.command(name='roll', help='Roll a dice with x sides y times, by default x=6, y=1. Usage: !roll [x] [y]')
async def roll(ctx, sides=6, times=1):
    numbers = np.random.randint(1, sides+1, times)
    text = ""
    for n in numbers:
        text += str(n)
        text += " "
    # Removing the final space
    text = text[0:-1]
    if len(text) <= 2000:
        await ctx.send(text)
    else:
        await ctx.send("Maximum message size reached, please reduce either the number of sides or the number of times")


@bot.command(name='plot', help='Plot data from this server. Usage: !plot [x] [y] where x is the choice of plot, 1 for'
                               'total messages, 2 for total words, 3 for filtered words. If option 3 has been chosen'
                               'then [y] must be given which should just be a sequence of words')
async def plot(ctx, choice, *, filterwords=None):
    # TODO: add checks on values of choice and filterwords.
    # Splitting up the filterwords and making it a list
    if filterwords:
        if choice == 1 or choice == 2:
            await ctx.send(f"Can't use filterwords with option {choice}")
            return
        words = filterwords.split()
        data_analysis.analyse(int(choice), words)
    else:
        data_analysis.analyse(int(choice))

    await ctx.send(file=discord.File('plot.png'))


@bot.command(name='update_messages', help='updates the internal file with all messages that is mostly used for plotting'
                                          '')
async def update_messages(ctx):
    await ctx.send("Started updating messages")

    author = []
    date = []
    content = []

    async for message in ctx.channel.history(limit=None, oldest_first=True):
        author.append(message.author)
        date.append(message.created_at.date())
        content.append(message.content)
    data = pd.DataFrame(data=np.array([author, date, content]).T, columns=["Author", "Date", "Content"])
    data.to_csv('data.csv', index=False)

    await ctx.send("Finished updating messages!")



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
# Bot has started so we can log that
print("Bot has started!")

check_queue.start()
bot.run(TOKEN)
