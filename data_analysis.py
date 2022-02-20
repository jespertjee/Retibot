import numpy as np
from matplotlib.pyplot import figure, show
import pandas as pd
import re

def extract_data():
    """"
    Function to extract data from the file and put it in a nice format

    :returns : transformed data in a pandas dataframe and the all the unique names
    """
    filedata = pd.read_csv("Retihom.csv", encoding="utf8")

    # Converting date column to datetime object
    filedata['Date'] = pd.to_datetime(filedata['Date'], format='%d-%m-%y')

    # Adding delta day column necessary for plotting
    filedata['Delta_day'] = filedata['Date'] - filedata['Date'][0]

    # Getting all users in the chat
    names = filedata['Author'].unique()

    return filedata, names


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


def plot_messages(filedata, names):
    # Getting number of messages in chat
    data = filedata.groupby(['Author', 'Delta_day']).size()

    # Unstacking data and filling in the NaNs, this is done so we can do the cumsum later
    data = data.unstack(0)
    data = data.fillna(0)

    # Cumulative summing
    data = data.cumsum()

    fig = figure(figsize=(15, 10))
    frame = fig.add_subplot(1, 1, 1)
    for name in names:
        number = str(int(data[name][-1]))
        frame.plot(range(data.index.size), data[name], label=(name + f': {number} messages'))
    frame.set_ylim(bottom=0)
    frame.set_xlim(left=0)
    frame.grid()
    frame.set_ylabel("Messages")
    frame.set_xlabel("Days since " + filedata['Date'][0].strftime("%d/%m/%Y"))

    fig.legend(loc=2)
    fig.suptitle('Data for sum of messages')
    fig.savefig("plot.png")


def plot_words(filedata):
    data = get_total_words(filedata)

    fig = figure(figsize=(15, 10))
    frame = fig.add_subplot(1, 1, 1)
    for column in data.columns:
        number = str(int(data[column][-1]))
        frame.plot(range(data.index.size), data[column], label=(column[1] + f': {number} words'))
    frame.set_ylim(bottom=0)
    frame.set_xlim(left=0)
    frame.grid()
    frame.set_ylabel("Words")
    frame.set_xlabel("Days since " + filedata['Date'][0].strftime("%d/%m/%Y"))

    fig.legend(loc=2)
    fig.suptitle('Data for sum of words')
    fig.savefig("plot.png")

# TODO: process (custom) emoji's into words first so they can be processed properly
def plot_filter_words(filedata, filterwords, filterword_query):
    data = get_filter_word_count(filedata, filterword_query)

    fig = figure(figsize=(15, 10))
    frame = fig.add_subplot(1, 1, 1)
    for column in data.columns:
        number = str(int(data[column][-1]))
        frame.plot(range(data.index.size), data[column], label=(column[1] + f': {number} times said'))
    frame.set_ylim(bottom=0)
    frame.set_xlim(left=0)
    frame.grid()
    frame.set_ylabel("Word count")
    frame.set_xlabel("Days since " + filedata['Date'][0].strftime("%d/%m/%Y"))

    fig.legend(loc=2)
    fig.suptitle('Data for filtered words: ' + str(filterwords))
    fig.savefig("plot.png")


def plot_relative_filter_words(filedata, filterwords, filterword_query):
    # Getting filtered words and total words so we can divide them
    filterdata = get_filter_word_count(filedata, filterword_query)['filter_count']
    worddata = get_total_words(filedata)['word_number']

    # Dividing them and changing na's into 0's (since we divided by 0 a bunch of times)
    fraction = filterdata.divide(worddata)
    fraction = fraction.fillna(0)

    fig = figure(figsize=(20, 10))
    frame = fig.add_subplot(1, 1, 1)

    sortednames = fraction.iloc[-1].sort_values(0, ascending=False).index
    for name in sortednames:
        # Transforming values to log, except if they are 0
        number = float(fraction[name][-1])
        # Check if number is equal to 0
        if number == 0:
            frame.plot(range(fraction.index.size), fraction[name],label=(name + r': final fraction: 0'))
        else:
            lognumber = str(round(np.log10(number), 2))
            text = name + r' Final fraction: $10^{' + lognumber + r'}$'
            frame.plot(range(fraction.index.size), fraction[name], label=text)
    frame.set_yscale('log')
    frame.set_xlim(left=0)
    frame.grid()
    frame.set_ylabel("Fraction of words")
    frame.set_xlabel("Days since " + filedata['Date'][0].strftime("%d/%m/%Y"))

    fig.legend(loc=2)
    fig.suptitle('Data for filtered words: ' + str(filterwords))
    fig.subplots_adjust(left=0.25)
    fig.savefig("plot.png")


def analyse(choice, filterwords = None):
    filedata, names = extract_data()

    # Retrieving filter words
    if choice == 3 or 4:
        # We have to make the filterwords into a query for pandas count to undertand using '|'s
        if len(filterwords)==1:
            filterword_query = filterwords[0]
        else:
            filterword_query = filterwords[0]
            for word in filterwords[1::]:
                filterword_query += f"|{word}"

    if choice == 1:
        plot_messages(filedata, names)
    elif choice == 2:
        plot_words(filedata)
    elif choice == 3:
        plot_filter_words(filedata, filterwords, filterword_query)
    elif choice == 4:
        plot_relative_filter_words(filedata, filterwords, filterword_query)


if __name__ == "__main__":
    analyse(3, ['test', 'fun'])
