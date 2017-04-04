import tweepy
import ast
import json
#override tweepy.StreamListener to add logic to on_status
tweets = {}
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    def on_data(self, data):
    	global tweets
    	tweet = json.loads(data)
    	url = ""
    	if "urls" in tweet:
    		if "expanded_url" in tweet["urls"][0]:
    			url = tweet["urls"][0]["expanded_url"]
    	print tweet["id_str"]
    	tweets[tweet["id_str"]]={"text":tweet["text"],"user":tweet["user"]["screen_name"],"url":url}
    	print tweets
    	return True

    def on_error(self, status):
    	print "Error"
        print(status)

    def get_tweets(self):
    	return self.tweets