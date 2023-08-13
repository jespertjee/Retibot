from discord.ext import commands, tasks
import pandas as pd
import requests
import numpy as np
import datetime
import data_analysis
import importlib

utc = datetime.timezone.utc
# Updating at 3 AM UTC
time = datetime.time(hour=3, minute=0, tzinfo=utc)


class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_messages.start()

    def cog_unload(self):
        self.update_messages.cancel()

    # Update messages
    @tasks.loop(time=time)
    async def update_messages(self):
        author = []
        date = []
        content = []

        # Reading the last date to use to update the messages
        last_date = data_analysis.data['Date'].iloc[-1]
        # Need to use 1 day later, because that is how channel history works
        after_date = pd.to_datetime(last_date, format="%d/%m/%Y") + datetime.timedelta(days=1)

        today = pd.to_datetime(datetime.date.today(), format="%Y-%m-%d").to_pydatetime()
        
        # TODO: make the channel choice flexible
        channel = self.bot.get_channel(604694988978126879)

        
        await channel.send("Updating messages")
        # Reading messages after the last saved message but before the new date. We should not include too new data,
        # since else we would extract the wrong date on the next day.
        async for message in channel.history(limit=None, oldest_first=True, after=after_date, before=today):
            author.append(message.author)
            date.append(message.created_at.date())
            content.append(message.content)
        data = pd.DataFrame(data=np.array([author, date, content]).T, columns=["Author", "Date", "Content"])

        # Changing the date formatting
        data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
        data['Date'] = data['Date'].dt.strftime("%d/%m/%Y")

        # Concatting this data to the data already loaded
        data = pd.concat([data_analysis.data_original, data])

        data.to_csv("Retihom.csv", index=False)

        # Reloading the analysis cog such that the new data gets loaded
        importlib.reload(data_analysis)

        await channel.send("Finished updating messages")

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



    """
    @commands.Cog.listener()
    async def on_message(self, ctx):
        # Reposting wrong twitter links
        if 'https://twitter.com/' in ctx.content:
            text = 'https://vxtwitter.com/' + str(ctx.content[20::])
            print(text)
            await ctx.channel.send(text)
    """




async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
