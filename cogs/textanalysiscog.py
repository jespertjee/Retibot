from discord.ext import tasks, commands
import discord
import sys
from flair.data import Sentence
from flair.nn import Classifier
sys.path.append("..")



class TextAnalysisCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0
        self.tagger = Classifier.load('sentiment')


async def setup(bot):
    await bot.add_cog(TextAnalysisCog(bot))