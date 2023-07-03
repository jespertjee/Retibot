from discord.ext import tasks, commands
import discord
import sys
sys.path.append("..")
import data_analysis
import shlex


class AnalysisCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='plot',
                 help='Plot data from this server. Usage: !plot [x] [y] where x is the choice of plot, 1 for'
                      'total messages, 2 for total words, 3 for filtered words. If option 3 has been chosen'
                      'then [y] must be given which should just be a sequence of words')
    async def plot(self, ctx, choice, *, filterwords=None):
        # TODO: add checks on values of choice and filterwords.
        # Splitting up the filterwords and making it a list
        if filterwords:
            if choice == 1 or choice == 2:
                await ctx.send(f"Can't use filterwords with option {choice}")
                return
            # See
            # https://stackoverflow.com/questions/79968/split-a-string-by-spaces-preserving-quoted-substrings-in-python
            words = shlex.split(filterwords)
            data_analysis.analyse(int(choice), words)
        else:
            data_analysis.analyse(int(choice))

        await ctx.send(file=discord.File('plot.png'))


async def setup(bot):
    await bot.add_cog(AnalysisCog(bot))