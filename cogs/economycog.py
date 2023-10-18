from discord.ext import tasks, commands
import pandas as pd
import yfinance as yf
from currency_converter import ECB_URL, SINGLE_DAY_ECB_URL, CurrencyConverter
import datetime
import discord
import matplotlib.pyplot as plt
import os


time = datetime.time(hour=3, minute=0, tzinfo=datetime.timezone.utc)

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.c = CurrencyConverter(SINGLE_DAY_ECB_URL)
        self.finances = pd.read_csv("finances.csv")
        self.stocks = pd.read_csv("stocks.csv")
        self.counter = 0
        # update time

    @tasks.loop(time=time)
    async def update_currencies(self):
        self.c = CurrencyConverter(SINGLE_DAY_ECB_URL)

    @tasks.loop(time=time)
    async def save_all(self):
        self.finances.to_csv('finances.csv', index=False)

    @commands.command(name='currency', help='Currency conversion rate')
    async def currency(self, ctx, *, arg):
        argument = arg.split(' ')
        currency1 = argument[0]
        currency2 = argument[1]
        try:
            await ctx.send(f"1 {currency1} is equal to {self.c.convert(1, currency1, currency2):.2f} {currency2}")
        except:
            await ctx.send("Conversion not succecful, are you sure both currencies are valid?")

    @commands.command(name='price', help='Tells you the stock price of a certain ticker')
    async def price(self, ctx, *, arg):
        argument = arg.split(' ')
        ticker_name = argument[0]

        # Getting the ticker from Yahoo Finance
        ticker = yf.Ticker(ticker_name).info
        market_price = ticker['currentPrice']
        currency = ticker['financialCurrency']

        # Converting currency if necessary
        if len(argument) > 1:
            preferred_currency = argument[1]
            exchange_rate = self.c.convert(1, currency, preferred_currency)
        else:
            exchange_rate = 1
            preferred_currency = currency

        print(exchange_rate)
        await ctx.send(f"Current market price of {ticker_name} is "
                       f"{exchange_rate*market_price:.2f} {preferred_currency}")

    @commands.command(name='starting_bonus', help='Get your free 1000 EUR starting bonus')
    async def starting_bonus(self, ctx):
        if ctx.author.name in self.finances['Name'].values:
            await ctx.send("You have already received your 1000 EUR!")
        else:
            self.finances.loc[len(self.finances.index)] = [ctx.author.name, 100000.]
            await ctx.send("100000 EUR has been deposited into your account!")

    @commands.command(name='money', help='Display the amount of money you have')
    async def money(self, ctx):
        if ctx.author.name in self.finances['Name'].values:
            await ctx.send(f"You have {float(self.finances[self.finances['Name']==ctx.author.name]['Balance']):.2f} EUR!")
        else:
            await ctx.send("You do not have an account yet. Use !starting_bonus to get started")

    @commands.command(name='economy', help='Shows how much money everyone has')
    async def economy(self, ctx):
        embed = discord.Embed(title="Finances", description="Amount of money held by each person.")

        # Getting stock value
        stock_value =  self.stocks[['Name', 'Total_value']].groupby('Name').sum()

        # Adding stock value to personal finances
        sum_stocks_and_money = self.finances.merge(stock_value, on='Name')
        sum_stocks_and_money['Total'] = sum_stocks_and_money['Total_value'] + sum_stocks_and_money['Balance']

        sorted_data = sum_stocks_and_money.sort_values(by=['Total'], ascending=False, ignore_index=True)
        for i, row in sorted_data.iterrows():
            embed.add_field(name=f"{i + 1}. {row['Name']}: {row['Total']:.2f} EUR",
                            value=f'Money: {row["Balance"]:.2f} EUR\n Stocks: {row["Total_value"]:.2f} EUR',
                            inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='buy', help='Buy a stock at market price')
    async def buy(self, ctx, *, arg):
        # Extracting ticker name and amount
        argument = arg.split(' ')
        ticker_name = argument[0]
        amount = int(argument[1])

        # Check if amount is bigger than 0
        if amount>0:

            ticker = yf.Ticker(ticker_name).info
            market_price = ticker['currentPrice']
            currency = ticker['financialCurrency']

            # Converting the currency if necessary
            if currency != "EUR":
                market_price = self.c.convert(market_price, currency, "EUR")
            total_price = market_price * amount

            # Check if user has enough money
            user_money = float(self.finances[self.finances['Name']==ctx.author.name]['Balance'])

            if user_money > total_price:
                # Subtracting money already
                self.finances.loc[self.finances['Name']==ctx.author.name, 'Balance'] -= total_price
                # If the stock is already on the ledger, we can simply change it
                filt = ((self.stocks.Name == ctx.author.name) & (self.stocks.Ticker == ticker_name))
                if filt.any():
                    self.stocks.loc[filt, 'Amount'] += amount
                    self.stocks.loc[filt, "Current_price_per_stock"] = market_price
                    self.stocks.loc[filt, 'Total_value'] = self.stocks.loc[filt, 'Amount'] * market_price

                else:
                    new_row = pd.DataFrame([[ctx.author.name, ticker_name, market_price, amount, total_price]],
                                           columns=["Name", "Ticker", "Current_price_per_stock", "Amount",
                                                    "Total_value"])
                    self.stocks = pd.concat([self.stocks, new_row])

                self.stocks.to_csv("stocks.csv", index=False)
                await ctx.send(f"Bought {amount} of {ticker_name} for a total of {total_price:.2f} EUR!")
            else:
                await ctx.send(f"You do not have enough money to buy this much!")

        else:
            await ctx.send(f"You have to buy at least 1 stock.")

    @commands.command(name='sell', help='Sell a stock at market price')
    async def sell(self, ctx, *, arg):
        # Extracting ticker name and amount
        argument = arg.split(' ')
        ticker_name = argument[0]
        amount = int(argument[1])

        # Check if amount is bigger than 0
        if amount > 0:
            filt = ((self.stocks.Name == ctx.author.name) & (self.stocks.Ticker == ticker_name))
            # Check if person owns enough stock
            print(self.stocks.loc[filt, 'Amount'])
            if int(self.stocks.loc[filt, 'Amount']) >= amount:
                ticker = yf.Ticker(ticker_name).info
                market_price = ticker['currentPrice']
                currency = ticker['financialCurrency']

                # Converting the currency if necessary
                if currency != "EUR":
                    market_price = self.c.convert(market_price, currency, "EUR")
                total_price = market_price * amount


                # Adding money already
                self.finances.loc[self.finances['Name'] == ctx.author.name, 'Balance'] += total_price

                # Removing stock from ledger
                filt = ((self.stocks.Name == ctx.author.name) & (self.stocks.Ticker == ticker_name))

                self.stocks.loc[filt, 'Amount'] -= amount
                self.stocks.loc[filt, "Current_price_per_stock"] = market_price
                self.stocks.loc[filt, 'Total_value'] = self.stocks.loc[filt, 'Amount'] * market_price

                self.stocks.to_csv("stocks.csv", index=False)
                await ctx.send(f"Sold {amount} of {ticker_name} for a total of {total_price:.2f} EUR!")
            else:
                await ctx.send(f"You are trying to sell more stocks than you own!")

        else:
            await ctx.send(f"You have to sell at least 1 stock.")

    @commands.command(name='portfolio', help='Check your portfolio')
    async def portfolio(self, ctx):
        data = self.stocks[self.stocks['Name'] == ctx.author.name]

        # Making a pie chart
        fig, ax = plt.subplots()
        ax.pie(data['Total_value'], labels=data['Ticker'], autopct='%1.1f%%')

        # Dynamic naming
        name = f"pie{self.counter}.png"
        self.counter += 1
        fig.savefig(name)

        embed = discord.Embed(title=f"Portfolio - {ctx.author.name}", description="", )


        for i, row in data.iterrows():
            if row.Amount>0:
                embed.add_field(name=f"{row['Ticker']} - {row['Amount']} stock(s) - Worth {row['Total_value']:.2f} EUR",
                                value='', inline=False)
        await ctx.send(embed=embed, file=discord.File(name))
        os.remove(name)




async def setup(bot):
    await bot.add_cog(EconomyCog(bot))