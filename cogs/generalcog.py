from discord.ext import commands
import pandas as pd
import requests


class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='update_messages', help='updates the internal file with all messages that is mostly used for plotting'
                                              '')
    async def update_messages(self, ctx):
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

    # TODO: tons of edge cases I havent added errors for here, should do that
    @commands.command(name='define', help='Define a word using google dictionary')
    async def define(self, ctx, *arg):
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

    @commands.command(name='roll', help='Roll a dice with x sides y times, by default x=6, y=1. Usage: !roll [x] [y]')
    async def roll(self, ctx, sides=6, times=1):
        numbers = np.random.randint(1, sides + 1, times)
        text = ""
        for n in numbers:
            text += str(n)
            text += " "
        # Removing the final space
        text = text[0:-1]
        if len(text) <= 2000:
            await ctx.send(text)
        else:
            await ctx.send(
                "Maximum message size reached, please reduce either the number of sides or the number of times")




def setup(bot):
    bot.add_cog(GeneralCog(bot))