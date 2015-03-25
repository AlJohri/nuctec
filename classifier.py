from __future__ import division

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split

from models import ctecs

from utils import group_ctecs_by_course_id
grouped_course_ctecs = group_ctecs_by_course_id()

courses = []
data = []
target = []

for course_id, course_ctecs in grouped_course_ctecs.iteritems():
	cur_text = "\n".join([course_ctec['adjectives'] for course_ctec in course_ctecs]).replace("/", " ")
	avg_challenge = sum([float(course_ctec['question3_average_rating']) for course_ctec in course_ctecs if course_ctec['question3_average_rating'] != ""])/len(filter(lambda x: x != "", course_ctecs))
	courses.append(course_id)
	data.append(cur_text)
	target.append(avg_challenge)

mean_split_val = sum(target)/len(target)
target = [0 if x < mean_split_val else 1 for x in target]

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

naive_bayes = MultinomialNB(alpha=1.0, fit_prior=True)
# vectorizer = TfidfVectorizer(tokenizer=LemmaTokenizer(), max_df=0.5, min_df=0.1)
vectorizer = TfidfVectorizer(min_df=.1, max_df=.6, stop_words='english')

data = vectorizer.fit_transform(data)
print data.shape

X_train, X_test , Y_train, Y_test = train_test_split(data, target, test_size=0.2)
print X_train.shape, X_test.shape, len(Y_train), len(Y_test)

naive_bayes.fit(X_train, Y_train)
print naive_bayes.score(X_test, Y_test)

cross_val_score(naive_bayes, data, target, scoring='accuracy', verbose=1, cv=5)

terms = vectorizer.get_feature_names()
t1 = naive_bayes.feature_log_prob_[0] # P(x_i|y0)
t2 = naive_bayes.feature_log_prob_[1] # P(x_i|y1)

for term, score in [(terms[i],t1[i]) for i in np.array(t1).argsort()][:20]:
	print term, score

print "\n\n-------------------------------\n\n"

for term, score in [(terms[i],t2[i]) for i in np.array(t2).argsort()][:20]:
	print term, score
