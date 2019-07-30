import tweepy
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import json
import statistics
import time
import threading
import sys
import keyboard
import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from tweetDefs import *
from auths import *
from config import *

tracker = [candidate1, candidate2]
analyzer = SentimentIntensityAnalyzer()
x_len = round(minutes * 60 * 1 / interval)
X = np.arange(minutes, 0, -interval / 60)
Y1 = [None] * x_len
Y2 = [None] * x_len
Y_range = 1
positive, negative, neutral, count = 0, 0, 0, 0
sentiments = [0]
startTime = time.time()
error = 0

csv = open(candidate1 + 'Data.csv', "w")
columnTitleRow = "candidate, vsentiment, tsentiment, location, user, time, tweet\n"
csv.write(columnTitleRow)

plt.style.use('seaborn')
plt.ion()
ax = plt.axes(xlim=(0, minutes), ylim=(-Y_range, Y_range))
line1 = ax.plot([], [], 'k-', lw=2)[0]
line2 = ax.plot([], [], lw=2)[0]

plt.ylabel('Sentiment')
plt.xlabel('Minutes')
plt.title('Tracking: ' + str(candidate1))


def close_looping():
    csv.close()
    sys.exit(0)


def graph_tweets():
    global positive, negative, neutral, Y_range, startTime, error

    while True:
        if keyboard.is_pressed('c'):
            csv.close()
            sys.exit(0)

        if time.time() - startTime + error >= interval:
            error += time.time() - startTime - interval
            startTime = time.time()
            Y1.append(statistics.mean(sentiments[-average1:]))
            del Y1[0]
            Y2.append(statistics.mean(sentiments[-average2:]))
            del Y2[0]

            line1.set_data(X, Y1)
            line2.set_data(X, Y2)

            plt.show()
            plt.pause(0.000001)


def log_tweet(dict_data):
    global positive, negative, neutral, count, Y_range

    user = dict_data["user"]["screen_name"]
    location = get_location(dict_data)
    tweet = get_tweet(dict_data)

    vSentiment = analyzer.polarity_scores(tweet)["compound"]
    tSentiment = TextBlob(tweet).sentiment.polarity

    if vSentiment > 0:
        sentiments.append(1)
        positive += 1
        count += 1
    elif vSentiment < 0:
        sentiments.append(-1)
        negative += 1
        count += 1
    else:
        sentiments.append(0)
        neutral += 1
        count += 1
    del sentiments[0]

    if tSentiment > 0:
        sentiments.append(1)
        positive += 1
        count += 1
    elif tSentiment < 0:
        sentiments.append(-1)
        negative += 1
        count += 1
    else:
        sentiments.append(0)
        neutral += 1
        count += 1
    if len(sentiments) > average2:
        del sentiments[0]

    print('***************************************')
    print(str(tweet))
    print('Vader: ' + str(vSentiment))
    print('Textblob: ' + str(tSentiment))

    print(negative, '|', neutral, '|', positive)

    if True:
        row = str(candidate1) + ', ' + str(vSentiment) + ', ' + str(tSentiment) + ', ' + str(location) + ', ' + \
              str(user) + ', ' + str(datetime.datetime.now().time()) + ', ' + tweet + '\n'
        csv.write(row)


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


def start_logger():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)

    myStream.filter(track=tracker, languages=['en'])


if __name__ == '__main__':
    x = threading.Thread(target=start_logger, args=())
    x.daemon = True
    x.start()
    graph_tweets()
