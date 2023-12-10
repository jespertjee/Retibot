import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import os

# Logging
import logging
import sys


root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)



# Generic bot settings
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def main():
    async with bot:
        await bot.load_extension('cogs.musiccog')
        await bot.load_extension('cogs.analysiscog')
        await bot.load_extension('cogs.generalcog')
        #await bot.load_extension('cogs.textanalysiscog')
        #await bot.load_extension('cogs.economycog')
        await bot.start(TOKEN)

asyncio.run(main())
