# coding: utf-8

### Set Twitter and MonkeyLearn API credentials
# TWITTER SETTINGS
# Credentials to consume Twitter API
TWITTER_CONSUMER_KEY = 'gPFX6uLLPSq1YNV3UvOOmxBm9'
TWITTER_CONSUMER_SECRET = 'A9OFNbEcGFBfV0GNt9dwx2AWncPRrcGBbueVzdl8e3FEdd1EJk'
TWITTER_ACCESS_TOKEN_KEY = '1486245986-QrZJp6vH6DDzjMJXUCQ0y5sl9eiCJVLRv30agdq'
TWITTER_ACCESS_TOKEN_SECRET = 'lzXe6UKt8vCPQOR5WesgErMJ8Ip0XpNvhhYLgEmStfF6r'

BING_KEY = 'b1bf79575cfe4a27b972105804809a30'
EXPAND_TWEETS = True

# This is the twitter user that we will be profiling using our news classifier.


TWITTER_USERS = ['NYT','washingtonpost', 'WSJ', 'BBC', 'YahooNews']
### Get user data with Twitter API
import multiprocessing.dummy as multiprocessing
from multiprocessing import Pool
# tweepy is used to call the Twitter API from Python
import tweepy
import re
from monkey_learn import *
import datetime
import time
from MyStreamListener import *

# Authenticate to Twitter API
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

listen = MyStreamListener()
stream = tweepy.Stream(auth, listen)

from random import shuffle


def get_friends_descriptions(api, twitter_account, max_users=100):
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

#potential to parallelize
def get_tweets(api, twitter_user, tweet_type='timeline', max_tweets=200, min_words=5):
    print "TWITTER USER: "+twitter_user
    tweets = []
    
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
        
        full_tweets.extend(current)
    
    [tweets.append({"Text":re.sub(r'(https?://\S+)', '', tweet.text), "Favorites":tweet.favorite_count, "Retweets":tweet.retweet_count, "url":"https://twitter.com/"+twitter_user+"/status/"+tweet.id_str,"Created_at":tweet.created_at}) for tweet in full_tweets]

    print "TWEETS "+twitter_user
    date = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    tweets.append(str(date))
    #write tweets to file
    f = open("static/"+twitter_user+".txt",'w+')
    f.write(str(tweets))
    f.close()
    return tweets

def _bing_search(query):
    
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


def _expand_text(text):
    result = text + u"\n" + _bing_search(text)
    print result
    return result


def expand_texts(texts):
    
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

def get_all_tweets():
    
    jobs = []
    for twitter_user in TWITTER_USERS:
        p = multiprocessing.Process(target=get_tweets, args = (api, twitter_user, 'timeline',1000))
        jobs.append(p)
        p.start()




if __name__ == '__main__':
    # Get the descriptions of the people that twitter_user is following.
    #descriptions = get_friends_descriptions(api, TWITTER_USER, max_users=300)
    #print "DESCRIPTIONS"
    #stream.filter(follow=TWITTER_USERS,async=True)
    #print descriptions

    tweets = []
    start = time.time()
    get_all_tweets()
    end = time.time()
    print "Parallel: "
    print (end-start)

    '''
    print "--------------SEQUENTIAL STARTING------------"
    start = time.time()
    for twitter_user in TWITTER_USERS:
        get_tweets(api, twitter_user, 'timeline', 1000)
    end = time.time()
    print "Sequential: "
    print (end-start)
    '''
    
   


