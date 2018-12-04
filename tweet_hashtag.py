from textblob import TextBlob
import json
import tweepy
from tweepy import OAuthHandler
import re
from collections import defaultdict
class TwitterClient(object):
    ''''
    Generic Twitter Class for sentiment analysis.
    '''

    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = 'e1I0CSqgSOGxhH940cey1PR50'
        consumer_secret = 'APZE7kT2MgJsledQszLbNVcZZEhCUDX3NKAseXTjnsEcggUAkf'
        access_token = '876294238144786432-Q9PfwxPd4T7OdYO9hXiFyVDO38Q8jZV'
        access_token_secret = 'e0RhKgnLLyHnEOrWS92Tw0pKv5hWrN3chjp4Azm4NayOG'

        # attempt authentication
        try:
            # create OAuthHandler object
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            # set access token and secret
            self.auth.set_access_token(access_token, access_token_secret)
            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
            print(self.api.rate_limit_status()['resources']['search'])
        except:
            print("Error: Authentication Failed")

    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment 1,2,3 = Neutral, positive, negative
        if analysis.sentiment.polarity > 0:
            return 2
        elif analysis.sentiment.polarity == 0:
            return 1
        else:
            return 3

    def get_tweets(self, query, count=1000):

        # Maximum number of tweets we want to collect
        maxTweets = 500
        # The twitter Search API allows up to 100 tweets per query
        tweetsPerQry = 100

        tweets = []
        hashtags_dict = {}
        hashtags_dict_sent = {}
        max_id = -1
        tweetCount = 0
        while tweetCount < maxTweets:
            try:
                # Look for more tweets, resuming where we left off
                if max_id <= 0:
                    new_tweets = self.api.search(q=query, count=tweetsPerQry)
                else:
                    new_tweets = self.api.search(q=query, count=tweetsPerQry, max_id=str(max_id - 1))

                # If we didn't find any exit the loop
                if not new_tweets:
                    print("No more tweets found")
                    break

                # Write the JSON output of any new tweets we found to the output file
                for tweet in new_tweets:
                    # Make sure the tweet has place info before writing
                    if (tweetCount < maxTweets):
                        ##
                        parsed_tweet = {}
                        # saving text of tweet
                        parsed_tweet['text'] = tweet.text
                        # saving sentiment of tweet
                        # parsed_tweet['sentiment'] = self.get_tweet_sentiment(tweet.text)
                        hashtags = tweet.entities.get('hashtags')

                        for hashtag in hashtags:
                            if hashtag['text'] in hashtags_dict.keys():
                                hashtags_dict[hashtag['text']] += 1
                                hashtags_dict_sent[hashtag['text']].append(self.get_tweet_sentiment(tweet.text))
                            else:
                                hashtags_dict[hashtag['text']] = 1
                                hashtags_dict_sent[hashtag['text']] = [self.get_tweet_sentiment(tweet.text)]

                                # appending parsed tweet to tweets list
                        if tweet.retweet_count > 0:
                            # if tweet has retweets, ensure that it is appended only once
                            if parsed_tweet not in tweets:
                                tweets.append(parsed_tweet)
                        else:
                            tweets.append(parsed_tweet)
                        ##
                        tweetCount += 1

                # Display how many tweets we have collected
                print("Downloaded {0} tweets".format(tweetCount))

                # Record the id of the last tweet we looked at
                max_id = new_tweets[-1].id

            except tweepy.TweepError as e:
                # Print the error and continue searching
                print("some error : " + str(e))

        return hashtags_dict, hashtags_dict_sent


def main():
    # creating object of TwitterClient Class
    api = TwitterClient()
    # calling function to get tweets
    tweets = api.get_tweets(query='kansas city', count=100)

    sorted_hash = dict(sorted(tweets[0].items(), key=lambda kv: kv[1], reverse=True))

    #print("Hashtags counts = ", sorted_hash)
    #print("----")
    #print("Hashtags_sent_counts = ", tweets[1])
    sent_dict= dict(tweets[1])

    sent_dict_comp = dict()

    for k,v in sent_dict.items():
        count_1 = 0
        count_2= 0
        count_3= 0
        max_name=0
        max_val=0
        val_list=[]

        for x in v:

            if x == 1:
                count_1 +=1
            if x == 2:
                count_2 +=1
            if x == 3:
                count_3 +=1
        if count_1>= count_2 and count_1>=count_3:
            max_name= 1
            max_val= count_1
        elif count_2>= count_1 and count_2>=count_3:
            max_name = 2
            max_val = count_2
        elif count_3>= count_1 and count_3>=count_2:
            max_name = 3
            max_val = count_3
        percentage_sent= max_val/len(v)
        val_list.extend((max_name,percentage_sent))
        sent_dict_comp[k]=val_list
        # merging two dictionaries (hashtag: count, and hashtag:[sentiment, probability])
    merge_dict=defaultdict(list)
    for d in (sorted_hash, sent_dict_comp):  # you can list as many input dicts as you want here
        for key, value in d.items():
            merge_dict[key].append(value)



    merge_dict_list=list()
    for key, value in merge_dict.items():
        temp = [key, value]
        merge_dict_list.append(temp)

    final_dict = dict()
    keyDict = {'text', 'value', 'sentiment', 'perc_senti'}
    final_dict = dict([(key, []) for key in keyDict])
    all_dict = list()
    i = 0
    j = 1
    k = 0
    while i < len(merge_dict_list):
        final_dict['text'] = merge_dict_list[i][k]
        final_dict['value'] = merge_dict_list[i][j][k]
        final_dict['sentiment'] = merge_dict_list[i][j][j][k]
        final_dict['perc_senti'] = merge_dict_list[i][j][j][j]
        all_dict.append(final_dict.copy())
        i += 1

    json_begin = '['
    json_end = ']'
    with open("final_output.json", 'a') as fp:
        fp.write(json_begin)
        for my_dict in all_dict:
            json.dump(my_dict, fp)
            if my_dict != all_dict[-1]:
                fp.write(',')

        fp.write(json_end)




if __name__ == "__main__":
    # calling main function
    main()
