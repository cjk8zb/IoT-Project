import json
import logging
import re
import sys

import tweepy
from textblob import TextBlob

logging.basicConfig(format='%(message)s')


class TwitterClient(object):
    """
    Generic Twitter Class for sentiment analysis.
    """

    def __init__(self):
        """
        Class constructor or initialization method.
        """
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'e1I0CSqgSOGxhH940cey1PR50'
        consumer_secret = 'APZE7kT2MgJsledQszLbNVcZZEhCUDX3NKAseXTjnsEcggUAkf'
        access_token = '876294238144786432-Q9PfwxPd4T7OdYO9hXiFyVDO38Q8jZV'
        access_token_secret = 'e0RhKgnLLyHnEOrWS92Tw0pKv5hWrN3chjp4Azm4NayOG'

        # clean tween regular expression
        self.pattern = re.compile('(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+://\S+)')

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
            logging.info(self.api.rate_limit_status()['resources']['search'])
        except:
            logging.error("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        """
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        """
        return ' '.join(re.sub(self.pattern, " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        """
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        """
        # create TextBlob object of passed tweet text
        polarity = TextBlob(self.clean_tweet(tweet)).sentiment.polarity
        if polarity > 0:
            return 1.0
        if polarity < 0:
            return -1.0
        return 0

    def get_tweets(self, query):

        # Maximum number of tweets we want to collect
        max_tweets = 500
        # The twitter Search API allows up to 100 tweets per query
        tweets_per_query = 100

        tweets = []
        mapped_tags = {}
        max_id = -1
        tweet_count = 0
        while tweet_count < max_tweets:
            try:
                # Look for more tweets, resuming where we left off
                if max_id <= 0:
                    new_tweets = self.api.search(q=query, count=tweets_per_query)
                else:
                    new_tweets = self.api.search(q=query, count=tweets_per_query, max_id=str(max_id - 1))

                # If we didn't find any exit the loop
                if not new_tweets:
                    logging.info("No more tweets found")
                    break

                # Write the JSON output of any new tweets we found to the output file
                for tweet in new_tweets:
                    # Make sure the tweet has place info before writing
                    if tweet_count < max_tweets:
                        # saving text of tweet
                        tweet_text = tweet.text
                        hashtags = tweet.entities['hashtags']
                        if len(hashtags) > 0:
                            # saving sentiment of tweet
                            sentiment = self.get_tweet_sentiment(tweet_text)
                            for hashtag in hashtags:
                                key = hashtag['text']
                                tag = mapped_tags.get(key, {'text': key, 'value': 0, 'total_sentiment': 0.0})
                                tag['value'] += 1
                                tag['total_sentiment'] += sentiment
                                mapped_tags[key] = tag
                                # appending parsed tweet to tweets list
                            if tweet.retweet_count > 0:
                                # if tweet has retweets, ensure that it is appended only once
                                if tweet_text not in tweets:
                                    tweets.append(tweet_text)
                            else:
                                tweets.append(tweet_text)
                        ##
                        tweet_count += 1

                # Display how many tweets we have collected
                logging.info("Downloaded {0} tweets".format(tweet_count))

                # Record the id of the last tweet we looked at
                max_id = new_tweets[-1].id

            except tweepy.TweepError as e:
                # Print the error and continue searching
                logging.error("some error : " + str(e))

        return mapped_tags


def main():
    # creating object of TwitterClient Class
    api = TwitterClient()

    # calling function to get tweets
    tweets = api.get_tweets(query='kansas city')

    # sort tags and return top 25
    top_tags = sorted(tweets.values(), key=lambda k: k['value'], reverse=True)[:25]

    # convert sentiment from total to average
    for v in top_tags:
        v['sentiment'] = v['total_sentiment'] / v['value']

    # output json to stdout
    json.dump(top_tags, sys.stdout)

    # flush output
    sys.stdout.flush()


if __name__ == "__main__":
    # calling main function
    main()
