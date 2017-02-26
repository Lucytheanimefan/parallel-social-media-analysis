# We'll keep only English tweets and bios
from monkeylearn import MonkeyLearn
import requests
import json

MONKEYLEARN_TOKEN = '838e1f8d79394292671861fb5eca34bd5074b61c'
ml = MonkeyLearn(MONKEYLEARN_TOKEN)

MONKEYLEARN_CLASSIFIER_BASE_URL = 'https://api.monkeylearn.com/api/v1/categorizer/'
MONKEYLEARN_EXTRACTOR_BASE_URL = 'https://api.monkeylearn.com/api/v1/extraction/'

# This classifier is used to detect the tweet/bio's language
MONKEYLEARN_LANG_CLASSIFIER_ID = 'cl_hDDngsX8'

# This classifier is used to detect the tweet/bio's topics
MONKEYLEARN_TOPIC_CLASSIFIER_ID = 'cl_5icAVzKR'

# This extractor is used to extract keywords from tweets and bios
MONKEYLEARN_EXTRACTOR_ID = 'ex_y7BPYzNG'

### Detect language with MonkeyLearn API


#classify a list of texts in batch mode (much faster)
def classify_batch(text_list, classifier_id):
    print "IN CLASSIFY BATCH"
    """
    Batch classify texts
    text_list -- list of texts to be classified
    classifier_id -- id of the MonkeyLearn classifier to be applied to the texts
    """
    results = []
    
    step = 250
    for start in xrange(0, len(text_list), step):
        end = start + step

        data = {'text_list': text_list[start:end]}

        response = requests.post(
            MONKEYLEARN_CLASSIFIER_BASE_URL + classifier_id + '/classify_batch_text/',
            data=json.dumps(data),
            headers={
                'Authorization': 'Token {}'.format(MONKEYLEARN_TOKEN),
                'Content-Type': 'application/json'
        })
        print "response"
        print response
        
        try:
            results.extend(response.json()['result'])
        except:
            print response.text
            raise

    print "Results:"
    print results
    return results


def filter_language(texts, language='English'):
    
    # Get the language of the tweets and bios using Monkeylearn's Language classifier
    lang_classifications = classify_batch(texts, MONKEYLEARN_LANG_CLASSIFIER_ID)

    print "Classifications:"
    print lang_classifications
    
    # Only keep the descriptions that are writtern in English.
    lang_texts = [
        text
        for text, prediction in zip(texts, lang_classifications)
        if prediction[0]['label'] == language
    ]

    return lang_texts


#descriptions_english = filter_language(descriptions)
#print "Descriptions found: {}".format(len(descriptions_english))


#tweets_english = filter_language(tweets)
#print "Tweets found: {}".format(len(tweets_english))


### Expand context of the data

# The following section is optional. You can use Bing search to expand the context of the data to obtain better classification accuracy.
# 

def extract_keywords(text_list, max_keywords):
    results = []
    step = 250
    for start in xrange(0, len(text_list), step):
        end = start + step

        data = {'text_list': text_list[start:end],
                'max_keywords': max_keywords}

        response = requests.post(
            MONKEYLEARN_EXTRACTOR_BASE_URL + MONKEYLEARN_EXTRACTOR_ID + '/extract_batch_text/',
            data=json.dumps(data),
            headers={
                'Authorization': 'Token {}'.format(MONKEYLEARN_TOKEN),
                'Content-Type': 'application/json'
        })

        try:
            results.extend(response.json()['result'])
        except:
            print response.text
            raise

    return results

### Detect the topics with MonkeyLearn API

from collections import Counter

def category_histogram(texts, short_texts):
    
    # Classify the bios and tweets with MonkeyLearn's news classifier.
    topics = classify_batch(texts, MONKEYLEARN_TOPIC_CLASSIFIER_ID)
    
    # The histogram will keep the counters of how many texts fall in
    # a given category.
    histogram = Counter()
    samples = {}

    for classification, text, short_text in zip(topics, texts, short_texts):

        # Join the parent and child category names in one string.
        category = classification[0]['label']
        probability = classification[0]['probability']
        
        if len(classification) > 1:
            category += '/' + classification[1]['label']
            probability *= classification[1]['probability']
        
        MIN_PROB = 0.0
        # Discard texts with a predicted topic with probability lower than a treshold
        if probability < MIN_PROB:
            continue
        
        # Increment the category counter.
        histogram[category] += 1
        
        # Store the texts by category
        samples.setdefault(category, []).append((short_text, text))
        
    return histogram, samples

'''
# Classify the expanded bios of the followed users using MonkeyLearn, return the historgram
descriptions_histogram, descriptions_categorized = category_histogram(expanded_descriptions, descriptions_english)

# Print the catogories sorted by most frequent
for topic, count in descriptions_histogram.most_common():
    print count, topic


# Classify the expanded tweets using MonkeyLearn, return the historgram
tweets_histogram, tweets_categorized = category_histogram(expanded_tweets, tweets_english)

# Print the catogories sorted by most frequent
for topic, count in tweets_histogram.most_common():
    print count, topic

### Get the keywords of each category with MonkeyLearn API

joined_texts = {}

for category in tweets_categorized:
    if category not in top_categories:
        continue
    
    expanded = 0
    joined_texts[category] = u' '.join(map(lambda t: t[expanded], tweets_categorized[category]))


keywords = dict(zip(joined_texts.keys(), extract_keywords(joined_texts.values(), 20)))

for cat, kw in keywords.iteritems():
    top_relevant = map(
        lambda x: x.get('keyword'),
        sorted(kw, key=lambda x: float(x.get('relevance')), reverse=True)
    )
    
    print u"{}: {}".format(cat, u", ".join(top_relevant))
'''