from textblob import TextBlob
from models import ctecs

easy_words = ["easy", "stress free", "painless", "little work", "no work", "breeze"]
hard_words = ["hard", "challenging", "difficult"]

for ctec in ctecs.find():
	ctec['easiness'] = sum([ctec['essay'].count(word) for word in easy_words])
	ctec['hardness'] = sum([ctec['essay'].count(word) for word in hard_words])
	# ctec['corrected_essay'] = unicode(TextBlob(ctec['essay']).correct())
	ctecs.save(ctec)