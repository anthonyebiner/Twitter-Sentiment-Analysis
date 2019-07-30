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
x_len = round(seconds * 1/interval)
X = np.arange(0, seconds, interval)
Y1 = [0] * x_len
Y2 = [0] * x_len
Y_range = 1
positive, negative, neutral, count = 0, 0, 0, 0
average = [0] * average2
startTime = time.time()
error = 0

csv = open(candidate1 + 'Data.csv', "w")
columnTitleRow = "candidate, sentiment, location, user\n"
csv.write(columnTitleRow)

plt.style.use('seaborn')
plt.ion()
fig = plt.figure()
ax = plt.axes(xlim=(0, seconds), ylim=(-Y_range, Y_range))
line1, = ax.plot([], [], lw=2)
line2, = ax.plot([], [], lw=2)

plt.ylabel('Sentiment')
plt.xlabel('Seconds')
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
            Y1.append(statistics.mean(average[-average1:]))
            del Y1[0]
            Y2.append(statistics.mean(average[-average2:]))
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

    if vSentiment > 0.05:
        average.append(1)
        positive += 1
        count += 1
    elif vSentiment < -0.05:
        average.append(-1)
        negative += 1
        count += 1
    else:
        average.append(0)
        neutral += 1
        count += 1
    del average[0]

    # print('***************************************')
    # print(str(tweet))
    # print('Vader: ' + str(vSentiment))

    print(negative, '|', neutral, '|', positive)

    if location is not None:
        row = str(candidate1) + ', ' + str(vSentiment) + ', ' + str(location) + ', ' + str(user) + ', ' + str(datetime.datetime.now().time()) + '\n'
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
