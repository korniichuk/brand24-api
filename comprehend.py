# -*- coding: utf-8 -*-

from configparser import NoOptionError
from operator import itemgetter

import boto3

def get_language(text, language_codes=None):
    """Determines the dominant language of the input text. For a list of
    languages that Amazon Comprehend can detect.
    Input:
        text -- A UTF-8 text string. Each string should contain at least
                20 characters and must contain fewer that 5,000 bytes of
                UTF-8 encoded characters (required | type: str);
        language_codes -- configparser config file with language coded
                          (not required | default: None).
    Output:
        language -- language name or language code, if no input
                    'language_codes' (type: str).
    """

    language = None

    comprehend = boto3.client('comprehend')
    try:
        r = comprehend.detect_dominant_language(Text=text)
    except Exception as exception:
        return language
    languages = r['Languages']
    language_dict = sorted(languages, key=itemgetter('Score'), reverse=True)[0]
    language_code = language_dict['LanguageCode']
    if language_codes == None:
        return language_code
    try:
        language = language_codes.get('code', language_code)
    except NoOptionError:
        return language_code
    else:
        return language

def get_sentiment(text, language_code='en'):
    """Inspects text and returns an inference of the prevailing sentiment
    (positive, neutral, mixed, or negative).
    Input:
        text -- UTF-8 text string. Each string must contain fewer that
                5,000 bytes of UTF-8 encoded characters (required | type: str);
        language_code -- language of text (not required | type: str |
                         default: 'en').
    Output:
        sentiment -- sentiment: positive, neutral, mixed, or negative
                     (type: str).
    """

    comprehend = boto3.client('comprehend')
    try:
        r = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    except Exception as exception:
        return 1
    sentiment = r['Sentiment'].lower()
    return sentiment

# Example. Get sentiment of text below:
# "I ordered a small and expected it to fit just right but it was a little bit
# more like a medium-large. It was great quality. It's a lighter brown than
# pictured but fairly close. Would be ten times better if it was lined with
# cotton or wool on the inside."
#text = "I ordered a small and expected it to fit just right but it was a \
#        little bit more like a medium-large. It was great quality. It's a \
#        lighter brown than pictured but fairly close. Would be ten times \
#        better if it was lined with cotton or wool on the inside."
#get_sentiment(text)
