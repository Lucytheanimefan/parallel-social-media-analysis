from flask import Flask, render_template
import flask
import os
from apscheduler.scheduler import Scheduler
import twitter_track
import atexit

app = Flask(__name__)
cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()

@cron.interval_schedule(hours=0.01) #every 6 minutes
def retrieve_tweets():
	print '-----RETRIEVE TWEET-----'
	twitter_track.get_all_tweets()

@app.route("/")
def home():
	return "Hello world"

atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)
