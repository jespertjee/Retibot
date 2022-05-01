from discord.ext import commands
from dotenv import load_dotenv
import os

# Generic bot settings
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

bot.load_extension("cogs.musiccog")
bot.load_extension("cogs.analysiscog")
bot.load_extension("cogs.generalcog")

print("Bot has started!")
bot.run(TOKEN)
