import os
from dotenv import load_dotenv
import discord
from discord.ext import commands,tasks
import numpy as np
import json
import asyncio
from youtube_dl import YoutubeDL
import requests



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

prefix = '!'

bot = commands.Bot(command_prefix=prefix)

# Paths of data files
emoji_source_path = 'emoji.json'
text_source_path = 'text.json'

# Writing in JSON files
def write_json(text,file):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(text, f)

# Load reactions
def reload_reactions():
    # Reading the JSON files
    with open(emoji_source_path,encoding='utf-8') as f:
        data = f.read()
        emoji_react_dic = json.loads(data)
    with open(text_source_path,encoding='utf-8') as f:
        data = f.read()
        text_react_dic = json.loads(data)
    return emoji_react_dic,text_react_dic

bot.emoji_react_dic,bot.text_react_dic = reload_reactions()

# Text reaction
def text_react(source,reaction):
    if source.lower() in bot.text_react_dic:
        # Finding the corresponding reaction and amending it
        bot.text_react_dic[source.lower()].append(reaction)
        with open(text_source_path, 'w', encoding='utf-8') as f:
            json.dump(bot.text_react_dic, f)
    else:
        bot.text_react_dic[source.lower()]=[reaction]
        with open(text_source_path, 'w', encoding='utf-8') as f:
            json.dump(bot.text_react_dic, f)
    # Opening source file

    return bot.text_react_dic

# Emoji reaction
def emoji_react(source,reaction):
    if source.lower() in bot.emoji_react_dic:
        # Finding the corresponding reaction and amending it
        bot.emoji_react_dic[source.lower()].append(reaction)
        with open(emoji_source_path, 'w', encoding='utf-8') as f:
            json.dump(bot.emoji_react_dic, f)
    else:
        bot.emoji_react_dic[source.lower()]=[reaction]
        with open(emoji_source_path, 'w', encoding='utf-8') as f:
            json.dump(bot.emoji_react_dic, f)

    return bot.emoji_react_dic

bot.queue = []

# Prints a message when the bot connects to discord
@bot.event
async def on_ready():
    # Setting voting channel
    bot.voting_channel = bot.get_channel(886558811064791041) #886558811064791041 for Retihom, 886554044657713153 for testing
    # Setting up users
    bot.jesper  = 173519627521884161
    bot.charles = 160459931093303297
    print('Connected!')


# Reacting to messages
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # Reacting to text messages
    for key in bot.emoji_react_dic:
        if key in message.content:
            for m in bot.emoji_react_dic[key]:
                await message.add_reaction(m)
    for key in bot.text_react_dic:
        if key in message.content:
            for m in bot.text_react_dic[key]:
                await message.channel.send(m)
        await bot.process_commands(message)
        return

    # See https://discordpy.readthedocs.io/en/latest/faq.html#why-does-on-message-make-my-commands-stop-working why this is necessary
    await bot.process_commands(message)

# Adding reactions
@bot.command(name='Add-emoji-reaction')
async def add_emoji_reaction(ctx,source,reaction):

    # Sending voting message
    text = str(ctx.message.author) + f" has requested \'{reaction}\' to be added as a reaction to \'{source}\', vote on it now!"
    msg = await bot.voting_channel.send(text)
    await msg.add_reaction('❎')
    await msg.add_reaction('✅')


    await asyncio.sleep(10)

    # see https://stackoverflow.com/questions/62965493/get-a-list-of-reactions-on-a-message-discord-py
    cache_msg = discord.utils.get(bot.cached_messages, id=msg.id) #or client.messages depending on your variable

    nay = cache_msg.reactions[0].count
    aye = cache_msg.reactions[1].count

    if nay>=aye:
        await bot.voting_channel.send('The vote from '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\' failed!")
        return

    # Checking if Charles or Jesper voted no
    jesper_veto  = False
    charles_veto = False
    async for user in cache_msg.reactions[0].users():
        if user.id==bot.jesper:
            jesper_veto = True
        if user.id==bot.charles:
            charles_veto = True

    # Seeing what scenario is true
    if jesper_veto and not charles_veto:
        await bot.voting_channel.send('Jesper vetoed the vote to '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\'")
    elif not jesper_veto and charles_veto:
        await bot.voting_channel.send('Melchett vetoed the vote to '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\'")
    elif jesper_veto and charles_veto:
        await bot.voting_channel.send('Melchett and Jesper vetoed the vote to '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\'")
    elif aye>nay:
        bot.emoji_react_dic = emoji_react(source,reaction)
        await bot.voting_channel.send('The vote from '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\' succeeded!")


@bot.command(name='Add-text-reaction')
async def add_text_reaction(ctx,source,reaction):
    # Sending voting message
    text = str(ctx.message.author) + f" has requested \'{reaction}\' to be added as a reaction to \'{source}\', vote on it now!"
    msg = await bot.voting_channel.send(text)
    await msg.add_reaction('❎')
    await msg.add_reaction('✅')


    await asyncio.sleep(10)

    # see https://stackoverflow.com/questions/62965493/get-a-list-of-reactions-on-a-message-discord-py
    cache_msg = discord.utils.get(bot.cached_messages, id=msg.id) #or client.messages depending on your variable

    nay = cache_msg.reactions[0].count
    aye = cache_msg.reactions[1].count

    if nay>=aye:
        await bot.voting_channel.send('The vote from '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\' failed!")
        return

    # Checking if Charles or Jesper voted no
    jesper_veto  = False
    charles_veto = False
    async for user in cache_msg.reactions[0].users():
        if user.id==bot.jesper:
            jesper_veto = True
        if user.id==bot.charles:
            charles_veto = True

    # Seeing what scenario is true
    if jesper_veto and not charles_veto:
        await bot.voting_channel.send('Jesper vetoed the vote to '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\'")
    elif not jesper_veto and charles_veto:
        await bot.voting_channel.send('Melchett vetoed the vote to '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\'")
    elif jesper_veto and charles_veto:
        await bot.voting_channel.send('Melchett and Jesper vetoed the vote to '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\'")
    elif aye>nay:
        bot.text_react_dic = text_react(source,reaction)
        await bot.voting_channel.send('The vote from '+str(ctx.message.author)+f" to add  \'{reaction}\' as a reaction to \'{source}\' succeeded!")

# Removing reactions
@bot.command(name='Remove-emoji-reaction')
async def remove_emoji_reaction(ctx,source,reaction):
    if source.lower() not in bot.emoji_react_dic:
        await ctx.send('Source message not found')
        return
    elif reaction not in bot.emoji_react_dic[source.lower()]:
        await ctx.send('Reaction message not found')
        return

    # Sending voting message
    text = str(ctx.message.author) + f" has requested \'{reaction}\' to be removed as a reaction to \'{source}\', vote on it now!"
    msg = await bot.voting_channel.send(text)
    await msg.add_reaction('❎')
    await msg.add_reaction('✅')


    await asyncio.sleep(10)

    # see https://stackoverflow.com/questions/62965493/get-a-list-of-reactions-on-a-message-discord-py
    cache_msg = discord.utils.get(bot.cached_messages, id=msg.id) #or client.messages depending on your variable

    nay = cache_msg.reactions[0].count
    aye = cache_msg.reactions[1].count

    if nay>=aye:
        await bot.voting_channel.send('The vote from '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\' failed!")
        return

    # Checking if Charles or Jesper voted no
    jesper_veto  = False
    charles_veto = False
    async for user in cache_msg.reactions[0].users():
        if user.id==bot.jesper:
            jesper_veto = True
        if user.id==bot.charles:
            charles_veto = True
    # Seeing what scenario is true
    if jesper_veto and not charles_veto:
        await bot.voting_channel.send('Jesper vetoed the vote to '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\'")
    elif not jesper_veto and charles_veto:
        await bot.voting_channel.send('Melchett vetoed the vote to '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\'")
    elif jesper_veto and charles_veto:
        await bot.voting_channel.send('Melchett and Jesper vetoed the vote to '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\'")
    elif aye>nay:
        if len(bot.emoji_react_dic[source.lower()])==1:
            bot.emoji_react_dic.pop(source.lower())
        else:
            bot.emoji_react_dic[source.lower()].remove(reaction)
        with open(emoji_source_path, 'w', encoding='utf-8') as f:
            json.dump(bot.emoji_react_dic, f)
        await bot.voting_channel.send('The vote from '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\' succeeded!")

@bot.command(name='Remove-text-reaction')
async def remove_text_reaction(ctx,source,reaction):
    if source.lower() not in bot.text_react_dic:
        await ctx.send('Source message not found')
        return
    elif reaction not in bot.text_react_dic[source.lower()]:
        await ctx.send('Reaction message not found')
        return

    # Sending voting message
    text = str(ctx.message.author) + f" has requested \'{reaction}\' to be removed as a reaction to \'{source}\', vote on it now!"
    msg = await bot.voting_channel.send(text)
    await msg.add_reaction('❎')
    await msg.add_reaction('✅')


    await asyncio.sleep(10)

    # see https://stackoverflow.com/questions/62965493/get-a-list-of-reactions-on-a-message-discord-py
    cache_msg = discord.utils.get(bot.cached_messages, id=msg.id) #or client.messages depending on your variable

    nay = cache_msg.reactions[0].count
    aye = cache_msg.reactions[1].count

    if nay>=aye:
        await bot.voting_channel.send('The vote from '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\' failed!")
        return

    # Checking if Charles or Jesper voted no
    jesper_veto  = False
    charles_veto = False
    async for user in cache_msg.reactions[0].users():
        if user.id==bot.jesper:
            jesper_veto = True
        if user.id==bot.charles:
            charles_veto = True

    # Seeing what scenario is true
    if jesper_veto and not charles_veto:
        await bot.voting_channel.send('Jesper vetoed the vote to '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\'")
    elif not jesper_veto and charles_veto:
        await bot.voting_channel.send('Melchett vetoed the vote to '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\'")
    elif jesper_veto and charles_veto:
        await bot.voting_channel.send('Melchett and Jesper vetoed the vote to '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\'")
    elif aye>nay:
        if len(bot.text_react_dic[source.lower()])==1:
            bot.text_react_dic.pop(source.lower())
        else:
            bot.text_react_dic[source.lower()].remove(reaction)
        with open(emoji_source_path, 'w', encoding='utf-8') as f:
            json.dump(bot.text_react_dic, f)
        await bot.voting_channel.send('The vote from '+str(ctx.message.author)+f" to remove  \'{reaction}\' as a reaction to \'{source}\' succeeded!")

# Error handling
@add_emoji_reaction.error
async def add_emoji_reaction_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please add both a source message and a reactions')
@add_text_reaction.error
async def add_text_reaction_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please add both a source message and a reactions')

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

@bot.command(name='play', help='To play song')
async def play(ctx,*,arg):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)


    if voice:
        if voice.is_playing() == False:
            with YoutubeDL({'format': 'bestaudio', 'noplaylist':'True','outtmpl': './downloads/song.%(ext)s'}) as ydl:
                try: requests.get(arg)
                except: info = ydl.extract_info(f"ytsearch:{arg}", download=True)['entries'][0]
                else: info = ydl.extract_info(arg, download=True)
            length,ext = info['duration'],info['ext']
            await ctx.send(f"Now playing {info['title']}.")

            #FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_delay_max 5', 'options': '-vn'}
            voice.play(discord.FFmpegPCMAudio(f"./downloads/song.{ext}"))
            await asyncio.sleep(int(length)+1)
            os.remove(f"./downloads/song.{ext}")
            if len(bot.queue)>0:
                arg = bot.queue[0]
                bot.queue.pop(0)
                await play(ctx=ctx,arg=arg)
        else:
            bot.queue.append(arg)
            await ctx.send("Added to the queue!")
    else:
        await join(ctx)
        await play(ctx=ctx,arg=arg)



@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


bot.run(TOKEN)
