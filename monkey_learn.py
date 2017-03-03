# We'll keep only English tweets and bios
from monkeylearn import MonkeyLearn
import requests
import json

MONKEYLEARN_TOKEN = '838e1f8d79394292671861fb5eca34bd5074b61c'
ml = MonkeyLearn(MONKEYLEARN_TOKEN)

# This classifier is used to detect the tweet/bio's language
MONKEYLEARN_LANG_CLASSIFIER_ID = 'cl_hDDngsX8'

# This classifier is used to detect the tweet/bio's topics
MONKEYLEARN_TOPIC_CLASSIFIER_ID = 'cl_5icAVzKR'

# This extractor is used to extract keywords from tweets and bios
MONKEYLEARN_EXTRACTOR_ID = 'ex_y7BPYzNG'

### Detect language with MonkeyLearn API

#works best in arrays of 25
def extract_topic(batched_array):
    print "A batch"
    print len(batched_array)
    res = ml.extractors.extract(MONKEYLEARN_EXTRACTOR_ID , [str(tweet['Text'].encode('ascii','ignore')) for tweet in batched_array if type(tweet) is dict and len(tweet['Text'])>1])
    return res.result

if __name__ == '__main__':
    print "hi"