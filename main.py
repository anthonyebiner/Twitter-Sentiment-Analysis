import tweepy
import matplotlib.pyplot as plt
import numpy as np
import json
import statistics
import time
import threading
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from tweetDefs import *
from auths import *
from config import *

analyzer = SentimentIntensityAnalyzer()
x_len = round(seconds * 1/interval)
X = np.arange(0, seconds, interval)
Y1 = [0] * x_len
Y2 = [0] * x_len
plt.ion()
graph = plt.plot(X, Y1)[0]
Y_range = 1
positive, negative, neutral, count = 0, 0, 0, 0
average = [0] * average2
startTime = time.time()
error = 0


def graph_tweets():
    print('running time function')
    global positive, negative, neutral, Y_range, startTime, error

    while True:
        if time.time() - startTime + error >= interval:
            error += time.time() - startTime - interval
            startTime = time.time()
            Y1.append(statistics.mean(average[-average1:]))
            del Y1[0]
            Y2.append(statistics.mean(average[-average2:]))
            del Y2[0]

            plt.clf()

            plt.ylabel('Sentiment')
            plt.xlabel('Seconds')
            plt.title('Tracking: ' + str(tracker))

            plt.ylim(-Y_range, Y_range)
            plt.xlim(0, seconds)

            plt.axhline(y=0, color='black', linestyle='-', linewidth='0.25')
            plt.plot(X, Y1, color='black')
            plt.plot(X, Y2, color='red')

            plt.show()
            plt.pause(0.00000001)
            print(negative, neutral, positive)


def log_tweet(dict_data):
    global positive, negative, neutral, count, Y_range

    # user = dict_data["user"]["screen_name"]
    # location = get_location(dict_data)
    tweet = get_tweet(dict_data)

    vSentiment = analyzer.polarity_scores(tweet)["compound"]
    # tSentiment = TextBlob(tweet).sentiment.polarity

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


def start_logger():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=auth, listener=myStreamListener)

    myStream.filter(track=tracker)


if __name__ == '__main__':
    x = threading.Thread(target=start_logger, args=())
    x.daemon = True
    x.start()

    graph_tweets()
