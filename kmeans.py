from utils import group_ctecs_by_course_id
grouped_course_ctecs = group_ctecs_by_course_id()

text = []
for course_id, course_ctecs in grouped_course_ctecs.iteritems():
	current_course_text = "\n".join([course_ctec['essay'] for course_ctec in course_ctecs])
	text.append(current_course_text)

import random
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

N_CLUSTERS = 2
reduce_dimensionality = True
k_means = KMeans(n_clusters=N_CLUSTERS, init='k-means++', max_iter=100, n_init=1, verbose=True)
vectorizer = TfidfVectorizer(tokenizer=LemmaTokenizer(), max_df=0.5, min_df=0.1)
# vectorizer = TfidfVectorizer(max_df=0.5, min_df=0.1) # stop_words='english'
lsa = TruncatedSVD(2)

vectors = vectorizer.fit_transform(text)
X = lsa.fit_transform(vectors)

km = k_means.fit(X)

k_means_labels = k_means.labels_
k_means_cluster_centers = k_means.cluster_centers_
k_means_labels_unique = np.unique(k_means_labels)
terms = vectorizer.get_feature_names()

for k in range(N_CLUSTERS):
    z = vectors.toarray()[k_means_labels == k]
    wordz_tfidf = [(terms[i], z[:,i].sum()) for i in range(z.shape[1])]
    wordz_tfidf = sorted(wordz_tfidf, key=lambda x: x[1], reverse=True )
    for word, score in wordz_tfidf[:100]:
    	print word, score
    print "\n\n\n"

fig,ax = plt.subplots(figsize=(15,10))

colors = [(random.random(), random.random(), random.random()) for x in range(N_CLUSTERS)]
for k, col in zip(range(N_CLUSTERS), colors):
    my_members = k_means_labels == k
    cluster_center = k_means_cluster_centers[k]
    points = ax.plot(X[my_members, 0], X[my_members, 1], 'w', markerfacecolor=col, marker='.', label='Cluster %i' % k)
    centers = ax.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col, markeredgecolor='k', markersize=6)

ax.set_title('KMeans')
ax.set_xticks(())
ax.set_yticks(())
ax.legend()

plt.show()