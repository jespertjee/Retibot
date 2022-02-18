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


def plot_messages(filedata, names):
    # Getting number of messages in chat
    data = filedata.groupby(['Author', 'Delta_day']).size()

    # Unstacking data and filling in the NaNs, this is done so we can do the cumsum later
    data = data.unstack(0)
    data = data.fillna(0)

    # Cumulative summing
    data = data.cumsum()

    fig = figure(figsize=(10,10))
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
    filedata['word_number'] = filedata['Content'].str.split().str.len()

    data = filedata[["Author", "word_number", "Delta_day"]]

    # Getting number of messages in chat
    data = data.groupby(['Author', 'Delta_day']).sum()

    # Unstacking data and filling in the NaNs, this is done so we can do the cumsum later
    data = data.unstack(0)
    data = data.fillna(0)

    # Cumulative summing
    data = data.cumsum()

    fig = figure(figsize=(10,10))
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
    filedata['filter_count'] = filedata['Content'].str.count(filterword_query, flags=re.IGNORECASE)

    data = filedata[["Author", "filter_count", "Delta_day"]]

    # Getting number of messages in chat
    data = data.groupby(['Author', 'Delta_day']).sum()

    # Unstacking data and filling in the NaNs, this is done so we can do the cumsum later
    data = data.unstack(0)
    data = data.fillna(0)

    # Cumulative summing
    data = data.cumsum()

    fig = figure(figsize=(10,10))
    frame = fig.add_subplot(1, 1, 1)
    for column in data.columns:
        number = str(int(data[column][-1]))
        frame.plot(range(data.index.size), data[column], label=(column[1] + f': {number} times said'))
    frame.set_ylim(bottom=0)
    frame.set_xlim(left=0)
    frame.grid()
    frame.set_ylabel("Words")
    frame.set_xlabel("Days since " + filedata['Date'][0].strftime("%d/%m/%Y"))

    fig.legend(loc=2)
    fig.suptitle('Data for filtered words: ' + str(filterwords))
    fig.savefig("plot.png")


def analyse(choice, filterwords = None):
    filedata, names = extract_data()

    # Retrieving filter words
    if choice == 3:
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


if __name__ == "__main__":
    analyse(3, ['test', 'fun'])
