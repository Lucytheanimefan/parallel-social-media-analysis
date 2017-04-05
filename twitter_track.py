# coding: utf-8

### Set Twitter and MonkeyLearn API credentials
# TWITTER SETTINGS
# Credentials to consume Twitter API
TWITTER_CONSUMER_KEY = 'gPFX6uLLPSq1YNV3UvOOmxBm9'
TWITTER_CONSUMER_SECRET = 'A9OFNbEcGFBfV0GNt9dwx2AWncPRrcGBbueVzdl8e3FEdd1EJk'
TWITTER_ACCESS_TOKEN_KEY = '1486245986-QrZJp6vH6DDzjMJXUCQ0y5sl9eiCJVLRv30agdq'
TWITTER_ACCESS_TOKEN_SECRET = 'lzXe6UKt8vCPQOR5WesgErMJ8Ip0XpNvhhYLgEmStfF6r'
########
TWITTER_CONSUMER_KEY1 = '9xCd6vJ8r9UOolGGWeqv2Ducz'
TWITTER_CONSUMER_SECRET1 = '0IKHLAXZxWdFQSkfkD4z1v98jqqwi6Nzj4D0gAZBS5QyRnyZLi'
TWITTER_ACCESS_TOKEN_KEY1 = '849248050094759936-PXdyoFglRNh9F8695gKMa97P3Vw1yFN'
TWITTER_ACCESS_TOKEN_SECRET1 = 'E2lgVYbrYh3TgaOTg0JY47a0xvAXFdiO22TtOqpLf5Wnp'


BING_KEY = 'b1bf79575cfe4a27b972105804809a30'
EXPAND_TWEETS = True

# This is the twitter user that we will be profiling using our news classifier.


TWITTER_USERS = ['NYT','washingtonpost', 'WSJ', 'BBC', 'YahooNews']
### Get user data with Twitter API
import multiprocessing.dummy as multiprocessing
from multiprocessing import Pool,Process
# tweepy is used to call the Twitter API from Python
import tweepy
from tweepy.streaming import StreamListener
import re
import time
import MyStreamListener
from MyStreamListener import *
from pytz import timezone
import datetime
from datetime import datetime
import signal 
from apscheduler.scheduler import Scheduler
import atexit
import newspaper
from newspaper import Article
from newspaper import news_pool
# Authenticate to Twitter API
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET)

auth1= tweepy.OAuthHandler(TWITTER_CONSUMER_KEY1, TWITTER_CONSUMER_SECRET1)
auth1.set_access_token(TWITTER_ACCESS_TOKEN_KEY1, TWITTER_ACCESS_TOKEN_SECRET1)

api = tweepy.API(auth)

listen = MyStreamListener(0)
stream = tweepy.Stream(auth, listen)

listen1 = MyStreamListener(1)
stream1 = tweepy.Stream(auth1, listen1)

api1 = tweepy.API(auth1)


stream_keys = {0:stream, 1:stream1}

from random import shuffle


cron = Scheduler()
cron.start()
# Explicitly kick off the background thread
def retrieve_tweets():
    time.sleep(10)
    print "-------------CRON JOB-----------"
    print listen.get_tweets()
    print listen1.get_tweets()


class MyTwitterTracker():
    def __init__(self,tweets):
        self.tweets = tweets

    def get_friends_descriptions(self, api, twitter_account, max_users=100):
        """
        Return the bios of the people that a user follows
        
        api -- the tweetpy API object
        twitter_account -- the Twitter handle of the user
        max_users -- the maximum amount of users to return
        """
        
        user_ids = api.friends_ids(twitter_account)
        shuffle(user_ids)
        
        following = []
        for start in xrange(0, min(max_users, len(user_ids)), 100):
            end = start + 100
            following.extend(api.lookup_users(user_ids[start:end]))
        
        descriptions = []
        for user in following:
            description = re.sub(r'(https?://\S+)', '', user.description)

            # Only descriptions with at least ten words.
            if len(re.split(r'[^0-9A-Za-z]+', description)) > 10:
                descriptions.append(description.strip('#').strip('@'))
        
        return descriptions

    def news_articles(self, tweets):
        for tweet in tweets:
            if len(tweet.entities["urls"])>2:
                url=tweet.entities["urls"][0]["expanded_url"]
            else:
                url = ""
            p = multiprocessing.Process(target=put_news_articles, args = (tweet.id_str,url))
            jobs.append(p)
            p.start()

    def put_news_articles(self, tweets):
        print "PUT NEWS ARTICLES"
        for tweet in tweets:
            id_str = tweet.id_str
            if len(tweet.entities["urls"])>1:
                url=tweet.entities["urls"][0]["expanded_url"]
                print url
            else:
                url = ""
                return
            a = Article(url,keep_article_html=True)
            a.download()
            a.parse()
            if id_str not in self.tweets:
                self.tweets[id_str]={}
            self.tweets[id_str]["article"]=a.text
            print "-------article-------"
            print self.tweets
            print "-------end article--------"
            return self.tweets

    #potential to parallelize
    def get_tweets(self, api, twitter_user, tweet_type='timeline', max_tweets=200, min_words=5):
        print "TWITTER USER: "+twitter_user
        processes = []
        full_tweets = []
        step = 200  # Maximum value is 200.
        for start in xrange(0, max_tweets, step):
            end = start + step
            
            # Maximum of `step` tweets, or the remaining to reach max_tweets.
            count = min(step, max_tweets - start)

            kwargs = {'count': count}
            if full_tweets:
                last_id = full_tweets[-1].id
                kwargs['max_id'] = last_id - 1

            if tweet_type == 'timeline':
                current = api.user_timeline(twitter_user, **kwargs)
            else:
                current = api.favorites(twitter_user, **kwargs)
            #print len(current)
            p = multiprocessing.Process(target=self.put_news_articles,args=(current,))
            processes.append(p)
            p.start()

            for tweet in current:
                id_str = tweet.id_str
                #print id_str
                if len(tweet.entities["urls"])>1:
                    url = tweet.entities["urls"][0]["expanded_url"]
                else:
                    url=""
                self.tweets[id_str]={"Text":re.sub(r'(https?://\S+)', '', tweet.text), "Favorites":tweet.favorite_count, "Retweets":tweet.retweet_count, "url":"https://twitter.com/"+twitter_user+"/status/"+tweet.id_str,"id":tweet.id_str,"Created_at":tweet.created_at,"expanded_url":url}
            #print self.tweets
            print "----------"

        print "TWEETS "+twitter_user
        #print tweets
        #fmt = "%Y-%m-%d %H:%M:%S %Z%z"
        #now_time = datetime.now(timezone('US/Eastern'))
        #tweets.append(now_time.strftime(fmt))
        #write tweets to file
        #f = open("static/"+twitter_user+".txt",'w+')
        #f.write(str(tweets))
        #f.close()
        #print self.tweets
        return self.tweets

    def tweet_replies(self, tweet_id, user):
        searched_tweets = []
        old_searched_tweets = []
        last_id = -1
        max_tweets=100
        query = "@"+user
        while len(searched_tweets)<max_tweets:
            count = max_tweets - len(old_searched_tweets)
            print count
            if count<0:
                break
            #try:
            new_tweets = api.search(q=query, count=count, max_id=str(last_id - 1))
            print "Old searched tweets" + str(len(old_searched_tweets))
            #print "New tweets"
            #print [[tweet.text, tweet.in_reply_to_user_id,tweet.in_reply_to_status_id] for tweet in new_tweets]
            if not new_tweets:
                print "breaking"
                break

            unused_tweets = new_tweets
            #for tweet in new_tweets:
            #    print tweet.in_reply_to_status_id
            new_tweets = [tweet.text for tweet in new_tweets if tweet_id == str(tweet.in_reply_to_status_id)]
            print new_tweets
            old_searched_tweets.extend(unused_tweets)
            searched_tweets.extend(new_tweets)
            last_id = unused_tweets[-1].id
            #print "last id: "+str(last_id)
        #print "DONE"
        #print searched_tweets
        return searched_tweets


    def _bing_search(self, query):
        
        MAX_EXPANSIONS = 5
        
        params = {
            'Query': u"'{}'".format(query),
            '$format': 'json',
        }
        
        response = requests.get(
            'https://api.datamarket.azure.com/Bing/Search/v1/Web',
            params=params,
            auth=(BING_KEY, BING_KEY)
        )
        
        try:    
            response = response.json()
        except ValueError as e:
            print e
            print response.status_code
            print response.text
            texts = []
            return
        else:
            texts = []
            for result in response['d']['results'][:MAX_EXPANSIONS]:
                texts.append(result['Title'])
                texts.append(result['Description'])

        return u" ".join(texts)


    def _expand_text(self, text):
        result = text + u"\n" + _bing_search(text)
        print result
        return result


    def expand_texts(self, texts):
        
        # First extract hashtags and keywords from the text to form the queries
        queries = []
        keyword_list = extract_keywords(texts, 10)
        for text, keywords in zip(texts, keyword_list):
            query = ' '.join([item['keyword'] for item in keywords])
            query = query.lower()
            tags = re.findall(r"#(\w+)", text)
            for tag in tags:
                tag = tag.lower()
                if tag not in query:
                    query = tag + ' ' + query
            queries.append(query)
            
        pool = multiprocessing.Pool(2)
        return pool.map(_expand_text, queries)

def get_tweet_general(tweet_tracker_object,api, twitter_user, tweet_type,max_num):
    tweet_tracker_object.get_tweets(api, twitter_user,tweet_type,max_num)


def get_all_tweets():
    
    jobs = []
    for twitter_user in TWITTER_USERS:
        tweets = {}
        tweet_track = MyTwitterTracker(tweets)
        p = multiprocessing.Process(target=get_tweet_general, args = (tweet_track, api1, twitter_user, 'timeline',10000))
        jobs.append(p)
        p.start()


def create_streams(num):
    stream_keys[num].filter(track=TWITTER_USERS,async=True)
    #print 'Starting'+str(num)
    #time.sleep(10)
    signal.pause()
    #print 'Exiting'+str(num)

atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    #cron.add_interval_job(retrieve_tweets,hours=0.001)
    #tweet_replies("844728600137875456","GiggukAZ")
    #get_tweets(api, TWITTER_USERS[0], 'timeline', 100)
    '''
    worker1 = Process(target=create_streams,args = (0,))
    worker2 = Process(target=create_streams, args=(1,))
    worker3= Process(target=retrieve_tweets, args=())
    worker1.start()
    worker2.start()
    worker3.start()
    '''
    get_all_tweets()
    
   


