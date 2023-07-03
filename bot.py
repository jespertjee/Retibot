import discord
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
import os

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
        await bot.start(TOKEN)

asyncio.run(main())
