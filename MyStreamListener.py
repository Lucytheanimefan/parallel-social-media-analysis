import tweepy
#override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)

    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status):
    	print "Error"
        print(status)