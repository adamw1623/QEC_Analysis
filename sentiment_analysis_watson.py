
import nltk
#nltk.download('vader_lexicon')
#nltk.download('punkt')
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from watson_developer_cloud import PersonalityInsightsV3
from watson_developer_cloud import WatsonApiException
from os.path import join, dirname

#Watson API Things
personality_insights = PersonalityInsightsV3(
    version='2018-03-19',
    iam_apikey='IacInRK_7IUlFQTMChf9IpYVamkwZ2pNQjpKmFEvwZe_',
    url='https://gateway.watsonplatform.net/personality-insights/api'
)

def PersonalityScores(column):
	print("Watson")
	openness_raw = []
	conscientiousness_raw = []
	extraversion_raw = []
	agreeableness_raw = []
	neuroticism_raw = []

	openness_perc = []
	conscientiousness_perc = []
	extraversion_perc = []
	agreeableness_perc = []
	neuroticism_perc = []
	'''
	Keys for the traits...
	'big5_openness'
    'big5_conscientiousness'
	'big5_extraversion'
	'big5_agreeableness'
	'big5_neuroticism'
	'''
	for entry in column:
		numFound = 0
		profile = personality_insights.profile(
			entry,
			content_type = 'text/plain',
			content_language = 'en-US',
			raw_scores = True).get_result()
		personality = profile['personality']
		# print(personality)

		for i in personality:
			if 'big5_openness' in i['trait_id']:
				openness_raw.append(i['raw_score'])
				openness_perc.append(i['percentile'])
				numFound += 1

			elif 'big5_conscientiousness' in i['trait_id']:
				conscientiousness_raw.append(i['raw_score'])
				conscientiousness_perc.append(i['percentile'])
				numFound += 1

			elif 'big5_extraversion' in i['trait_id']:
				extraversion_raw.append(i['raw_score'])
				extraversion_perc.append(i['percentile'])
				numFound += 1

			elif 'big5_agreeableness' in i['trait_id']:
				agreeableness_raw.append(i['raw_score'])
				agreeableness_perc.append(i['percentile'])
				numFound += 1

			elif 'big5_neuroticism' in i['trait_id']:
				neuroticism_raw.append(i['raw_score'])
				neuroticism_perc.append(i['percentile'])
				numFound += 1
		
		if numFound != 5:
			raise ValueError('Not all big 5 scores generated')

	return opennness_raw, conscientiousness_raw, extraversion_raw, agreeableness_raw, neuroticism_raw, opennness_perc, conscientiousness_perc, extraversion_perc, agreeableness_perc, neuroticism_perc


def ColumnScoring(column):
     sentiments = []
     for entry in column:
         sid = SIA()
         sentiment = sid.polarity_scores(entry) ['pos']
         sentiments.append(sentiment)    
     return sentiments

def WordCounting(column):
    word_counts = []
    for entry in column:
        count = len(nltk.word_tokenize(entry))
        word_counts.append(count)
    return word_counts

def SentenceCounting(column):
    sent_counts = []
    for entry in column:
        count = len(nltk.sent_tokenize(entry))
        sent_counts.append(count)
    return sent_counts

def CEOspin(CEOScore,ContextScore):
    CEOSpin = []
    for i in range(len(CEOScore)):
        temp = CEOScore[i]-ContextScore[i]
        CEOSpin.append(temp)
    return CEOSpin

def CustomDict(column, dict):
    scores = []
    for entry in column:
        words = nltk.word_tokenize(entry)
        count = 0
        for word in words:
            if word in dict.values:
                count += 1
        scores.append(count)
    return scores



# =============================================================================
#                    I had trouble using the NLTK installer
#                  Make sure to download the Vader package too
# import nltk
# import ssl
# 
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
# 
# nltk.download()
# 
# =============================================================================




# =============================================================================
#  No longer working 
#from textblob import TextBlob
# 
# def ColumnScoring(series):
#     sentiments = []
#     for blob in series:
#         sentiment = TextBlob(blob)
#         sentiments.append(sentiment.sentiment.polarity)    
#     return sentiments
# =============================================================================