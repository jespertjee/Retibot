import numpy as np
from matplotlib.pyplot import figure, show
import pandas as pd
import re
import datetime

# Variables
# How many days the rolling windows should be
rolling_window_days = 90

# Loading the data TODO: there must be a better way to do this instead of just loading it like this
print("loaded Retihom.csv")
data_original = pd.read_csv("Retihom.csv", encoding="utf8")
# This data we will append stuff to
# TODO: do this nicer by instead changing the names in the rest of the file (or copying it there)
data = data_original.copy()


def get_bots(unique_names):
    """"
    Function to get o get the list of bots
    """


def add_delta_day(data, column_name: str = 'Date'):
    """"
    Function to add the delta day column in the data, which is simply a column with the amount of days since the
    first date in the column.

    :param data : the pandas dataframe containing all the discord messages
    :param column_name : the name of the date column, is 'date' by default

    :returns data : modified pandas dataframe with the aforementioned delta_day column
    """
    # Converting date column to pandas datetime
    data[column_name] = pd.to_datetime(data[column_name], format="%d/%m/%Y")
    # Adding delta day column necessary for plotting
    data['Delta_day'] = data[column_name] - data[column_name].iloc[0]

    return data


def get_unique_names(data, column_name: str = 'Author'):
    """"
    Function which returns all the unique names in the chat log, i.e. all the users that were in the chat

    :param data : the pandas dataframe containing all the discord messages
    :param column_name : the name of the author column, is 'author' by default

    :returns names : all the unique names in the file
    """
    return data[column_name].unique()

def get_filter_word_count(filedata, filterword_query):
    """"
    Function to get the absolute count of the filtered words in a pandas dataframe
    """
    filedata['filter_count'] = filedata['Content'].str.count(filterword_query, flags=re.IGNORECASE)

    data = filedata[["Author", "filter_count", "Delta_day"]]

    # Getting number of messages in chat
    data = data.groupby(['Author', 'Delta_day']).sum()

    # Unstacking data and filling in the NaNs, this is done so we can do the cumsum later
    data = data.unstack(0)
    data = data.fillna(0)

    # Cumulative summing
    data = data.cumsum()

    return data


def get_total_words(filedata):
    """"
    Function to get total words over time in a pandas dataframe
    """
    filedata['word_number'] = filedata['Content'].str.split().str.len()

    data = filedata[["Author", "word_number", "Delta_day"]]

    # Getting number of messages in chat
    data = data.groupby(['Author', 'Delta_day']).sum()

    # Unstacking data and filling in the NaNs, this is done so we can do the cumsum later
    data = data.unstack(0)
    data = data.fillna(0)

    # Cumulative summing
    data = data.cumsum()
    return data


def plot_general():
    """"
    Generic plot function
    """
    return


def plot_messages(filedata, plot_name):
    # Getting number of messages in chat
    data = filedata.groupby(['Author', 'Delta_day']).size()

    # Unstacking data and filling in the NaNs, this is done so we can do the cumsum later
    data = data.unstack(0)
    data = data.fillna(0)

    # Cumulative summing
    data = data.cumsum()


    fig = figure(figsize=(15, 10))
    frame = fig.add_subplot(1, 1, 1)

    sortednames = data.iloc[-1].sort_values(0, ascending=False).index
    # Days for plotting on the x-axis
    days = [(pd.to_datetime(filedata['Date'][0], format="%d/%m/%Y") + datetime.timedelta(days=i)) for i in
            range(data.index.size)]
    for column in sortednames:
        number = str(int(data[column][-1]))
        frame.plot(days, data[column], label=(column + f': {number} messages'))
    frame.set_ylim(bottom=0)
    frame.grid()
    frame.set_ylabel("Messages")
    frame.set_xlabel("Date")

    fig.legend(loc=2)
    fig.suptitle('Data for sum of messages')
    fig.savefig(plot_name)


def plot_words(filedata, plot_name):
    data = get_total_words(filedata)

    fig = figure(figsize=(15, 10))
    frame = fig.add_subplot(1, 1, 1)

    sortednames = data.iloc[-1].sort_values(0, ascending=False).index
    # Days for plotting on the x-axis
    days = [(pd.to_datetime(filedata['Date'][0], format="%d/%m/%Y") + datetime.timedelta(days=i)) for i in
            range(data.index.size)]
    for column in sortednames:
        number = str(int(data[column][-1]))
        frame.plot(days, data[column], label=(column[1] + f': {number} words'))
    frame.set_ylim(bottom=0)
    frame.grid()
    frame.set_ylabel("Words")
    frame.set_xlabel("Date")

    fig.legend(loc=2)
    fig.suptitle('Data for sum of words')
    fig.savefig(plot_name)


# TODO: process (custom) emoji's into words first so they can be processed properly
def plot_filter_words(filedata, plot_name, filterwords, filterword_query):
    data = get_filter_word_count(filedata, filterword_query)

    fig = figure(figsize=(15, 10))
    frame = fig.add_subplot(1, 1, 1)

    # Sorting
    sortednames = data.iloc[-1].sort_values(0, ascending=False).index
    # Days for plotting on the x-axis
    days = [(pd.to_datetime(filedata['Date'][0], format="%d/%m/%Y") + datetime.timedelta(days=i)) for i in
            range(data.index.size)]
    for name in sortednames:
        number = str(int(data[name][-1]))
        frame.plot(days, data[name], label=(name[1] + f': {number} times said'))

    frame.set_ylim(bottom=0)
    frame.grid()
    frame.set_ylabel("Word count")
    frame.set_xlabel("Date")

    fig.legend(loc=2)
    fig.suptitle('Data for filtered words: ' + str(filterwords))
    fig.savefig(plot_name)


def plot_relative_filter_words(filedata, plot_name, filterwords, filterword_query):
    # Getting filtered words and total words so we can divide them
    filterdata = get_filter_word_count(filedata, filterword_query)['filter_count']
    worddata = get_total_words(filedata)['word_number']

    # Dividing them and changing na's into 0's (since we divided by 0 a bunch of times)
    fraction = filterdata.divide(worddata)
    fraction = fraction.fillna(0)

    fig = figure(figsize=(20, 10))
    frame = fig.add_subplot(1, 1, 1)

    sortednames = fraction.iloc[-1].sort_values(0, ascending=False).index

    # Days for plotting on the x-axis
    days = [(pd.to_datetime(filedata['Date'][0], format="%d/%m/%Y") + datetime.timedelta(days=i)) for i in
            range(fraction.index.size)]
    for name in sortednames:
        # Transforming values to log, except if they are 0
        number = float(fraction[name][-1])
        # Check if number is equal to 0
        if number == 0:
            frame.plot(days, fraction[name], label=(name + r': final fraction: 0'))
        else:
            lognumber = str(round(np.log10(number), 2))
            text = name + r' Final fraction: $10^{' + lognumber + r'}$'
            frame.plot(days, fraction[name], label=text)
    frame.set_yscale('log')
    frame.grid()
    frame.set_ylabel("Fraction of words")
    frame.set_xlabel("Date")

    fig.legend(loc=2)
    fig.suptitle('Data for filtered words: ' + str(filterwords))
    fig.subplots_adjust(left=0.25)
    fig.savefig(plot_name)


def get_total_words_rolling(filedata):
    """"
    Function to get total words over a rolling week
    """
    filedata['word_number'] = filedata['Content'].str.split().str.len()

    data = filedata[["Author", "word_number", "Delta_day"]]

    # Getting number of messages in chat
    data = data.groupby(['Author', 'Delta_day']).sum()

    # Unstacking data and filling in the NaNs
    data = data.unstack(0)
    data = data.fillna(0)

    # Cumulative summing
    data = data.rolling(f'{rolling_window_days}d').sum()
    return data


def plot_relative_filter_words_week(filedata, plot_name, filterwords, filterword_query):
    # Getting the frequency of words
    filedata['filter_count'] = filedata['Content'].str.count(filterword_query, flags=re.IGNORECASE)

    data = filedata[["Author", "filter_count", "Delta_day"]]

    # Getting number of messages per day
    data = data.groupby(['Author', 'Delta_day']).sum()

    # Unstacking such that we have data for each day
    data = data.unstack(0)

    data = data.rolling(f'{rolling_window_days}d').sum()
    worddata = get_total_words_rolling(filedata)['word_number']

    # Dividing them and changing na's into 0's (since we divided by 0 a bunch of times)
    fraction = data.divide(worddata)
    fraction = fraction.fillna(0)

    fig = figure(figsize=(20, 10))
    frame = fig.add_subplot(1, 1, 1)

    sortednames = fraction.iloc[-1].sort_values(0, ascending=False).index

    # Days for plotting on the x-axis
    days = [(pd.to_datetime(filedata['Date'][0], format="%d/%m/%Y") + datetime.timedelta(days=i)) for i in
            range(fraction.index.size)]
    for name in sortednames:
        frame.plot(days, fraction[name], label=name[1])
    frame.grid()
    frame.set_ylabel("Fraction of words")
    frame.set_xlabel("Date")

    fig.legend(loc=2)
    fig.suptitle(f'{rolling_window_days} day rolling fraction for filtered words: ' + str(filterwords))
    fig.subplots_adjust(left=0.25)
    fig.savefig(plot_name)


def plot_absolute_filter_words_week(filedata, plot_name, filterwords, filterword_query):
    # Getting the frequency of words
    filedata['filter_count'] = filedata['Content'].str.count(filterword_query, flags=re.IGNORECASE)

    data = filedata[["Author", "filter_count", "Delta_day"]]

    # Getting number of messages per day
    data = data.groupby(['Author', 'Delta_day']).sum()

    # Unstacking such that we have data for each day
    data = data.unstack(0)

    data = data.rolling(f'{rolling_window_days}d').sum()

    fig = figure(figsize=(20, 10))
    frame = fig.add_subplot(1, 1, 1)

    sortednames = data.iloc[-1].sort_values(0, ascending=False).index

    # Days for plotting on the x-axis
    days = [(pd.to_datetime(filedata['Date'][0], format="%d/%m/%Y") + datetime.timedelta(days=i)) for i in
            range(data.index.size)]
    for name in sortednames:
        frame.plot(days, data[name], label=name[1])
    frame.grid()
    frame.set_ylabel("Count of words")
    frame.set_xlabel("Date")

    fig.legend(loc=2)
    fig.suptitle(f'{rolling_window_days} day rolling count for filtered words: ' + str(filterwords))
    fig.subplots_adjust(left=0.25)
    fig.savefig(plot_name)


def analyse(choice, plot_name, filterwords=None):
    filedata = add_delta_day(data)

    if choice == 1:
        plot_messages(filedata, plot_name)
    elif choice == 2:
        plot_words(filedata, plot_name)
    else:
        # Retrieving filter words by transforming them into a query
        # We have to make the filterwords into a query for pandas count to understand using '|'s
        if len(filterwords) == 1:
            filterword_query = filterwords[0]
        else:
            filterword_query = filterwords[0]
            for word in filterwords[1::]:
                filterword_query += f"|{word}"
        if choice == 3:
            plot_filter_words(filedata, plot_name, filterwords, filterword_query)
        elif choice == 4:
            plot_relative_filter_words(filedata, plot_name, filterwords, filterword_query)
        elif choice == 6:
            plot_relative_filter_words_week(filedata, plot_name, filterwords, filterword_query)
        elif choice == 5:
            plot_absolute_filter_words_week(filedata, plot_name, filterwords, filterword_query)


if __name__ == "__main__":
    analyse(3, ['test', 'fun'])
