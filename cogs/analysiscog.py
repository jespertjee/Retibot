from discord.ext import tasks, commands
import discord
import sys
sys.path.append("..")
import data_analysis
import shlex
import os


class AnalysisCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.counter = 0

    @commands.command(name='plot',
                 help='Plot data from this server. Usage: !plot [x] [y] where x is the choice of plot, 1 for'
                      'total messages, 2 for total words, 3 for filtered words, 4 for filtered word fraction, 5 for '
                      'rolling sum of filtered words and 6 for rolling fraction of filtered words. If option 3, 4, 5 '
                      'or 6 '
                      'has been chosen'
                      'then [y] must be given which should just be a sequence of words')
    async def plot(self, ctx, choice, *, filterwords=None):
        # TODO: add checks on values of choice and filterwords.

        # Plot name, so that we can do multiple commands without the plots overwriting each other
        plot_name = f"plot{self.counter}.png"
        self.counter += 1

        # Splitting up the filterwords and making it a list
        if filterwords:
            if choice == 1 or choice == 2:
                await ctx.send(f"Can't use filterwords with option {choice}")
                return
            # See
            # https://stackoverflow.com/questions/79968/split-a-string-by-spaces-preserving-quoted-substrings-in-python
            words = shlex.split(filterwords)
            data_analysis.analyse(int(choice), plot_name, words)
        else:
            data_analysis.analyse(int(choice), plot_name)

        await ctx.send(file=discord.File(plot_name))
        os.remove(plot_name)

async def setup(bot):
    await bot.add_cog(AnalysisCog(bot))