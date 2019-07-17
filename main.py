import tweepy
import pylab as plt
import matplotlib.pyplot as mplt
import numpy as np
import json
import re
import time
import statistics
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from config import *
import time

analyzer = SentimentIntensityAnalyzer()


def clean_tweet(dict_data):
    # return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", dict_data).split())
    return " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", dict_data).split())
    # return dict_data


def get_location(dict_data):
    if dict_data["user"]["location"] is not None:
        for abbreviation, state in states.items():
            if abbreviation in dict_data["user"]["location"] or state in dict_data["user"]["location"]:
                return state
    return None


def get_tweet(dict_data):
    if dict_data["truncated"]:
        return clean_tweet(dict_data["extended_tweet"]["full_text"])
    else:
        return clean_tweet(dict_data["text"])


x_len = 2000
average_len = 1000
average = [0] * average_len

X = np.linspace(0, x_len, x_len)
Y1 = [0] * x_len
Y2 = [0] * x_len

mplt.ion()
graph = mplt.plot(X, Y1)[0]

Y_range = 1

positive, negative, neutral, count = 0, 0, 0, 0

average1 = 100
average2 = 500

startTime = time.time()


def printit():
    global positive
    global negative
    global neutral
    global Y_range
    global startTime

    Y1.append(statistics.mean(average[-average1:]))
    del Y1[0]
    Y2.append(statistics.mean(average[-average2:]))
    del Y2[0]

    if time.time()-startTime >= 0.075:
        mplt.clf()
        mplt.ylim(-Y_range, Y_range)
        mplt.xlim(0, x_len + x_len/50)
        mplt.ylabel('Sentiment')
        mplt.xlabel('Tweets')
        mplt.axhline(y=0, color='black', linestyle='-', linewidth='0.25')
        mplt.plot(X, Y1, color='black')
        mplt.plot(X, Y2, color='red')
        mplt.show()
        mplt.pause(0.000001)
        startTime = time.time()

    print(negative, neutral, positive)


def graph_sentiment_rolling_average(sentiment):
    global positive
    global negative
    global neutral
    global count
    global Y_range

    if sentiment > 0.05:
        average.append(1)
        positive += 1
        count += 1
    elif sentiment < -0.05:
        average.append(-1)
        negative += 1
        count += 1
    else:
        average.append(0)
        neutral += 1
        count += 1
    del average[0]

    printit()


def log_tweet(dict_data):
    # user = dict_data["user"]["screen_name"]
    # location = get_location(dict_data)
    tweet = get_tweet(dict_data)

    vSentiment = analyzer.polarity_scores(tweet)["compound"]
    # tSentiment = TextBlob(tweet).sentiment.polarity

    graph_sentiment_rolling_average(vSentiment)
    # graph_sentiment_rolling_average(tSentiment)

    print('***************************************')
    print(str(tweet))
    print('Vader: ' + str(vSentiment))
    # print('TextBlob: ' + str(tSentiment))


class MyStreamListener(tweepy.StreamListener):
    def on_data(self, data):
        dict_data = json.loads(data)
        if 'truncated' in dict_data and 'text' in dict_data and 'user' in dict_data:
            log_tweet(dict_data)
        return True

    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False


if __name__ == '__main__':
    states = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
              "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
              "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
              "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
              "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
              "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
              "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
              "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
              "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
              "WI": "Wisconsin", "WY": "Wyoming"}

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)

    myStream.filter(track=['trump'])
