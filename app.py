from flask import Flask, render_template,send_from_directory, jsonify
import flask
import os
from apscheduler.scheduler import Scheduler
import twitter_track
import atexit
import text_analysis
from flask_cors import CORS

app = Flask(__name__)
cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()

CORS(app)

@cron.interval_schedule(hours=0.06) #every 6 minutes
def retrieve_tweets():
	twitter_track.get_all_tweets()

@app.route("/")
def home():
	return render_template("index.html")


@app.route('/<media_site>', methods=['GET','POST'])
def text_file(media_site):
    #do your code here
    return send_from_directory(app.static_folder, media_site+".txt")


@app.route("/get_tweets", methods = ["GET"])
def get_tweets():
	#print text_analysis.pure_text_from_file("NYT.txt")
	return str(text_analysis.pure_text_from_file("NYT.txt"))
#@app.route('/.txt', methods)
#def static_from_root():
#    return send_from_directory(app.static_folder, request.path[1:])



atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port, threaded=True)
