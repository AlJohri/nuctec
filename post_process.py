from models import ctecs

easy_words = ["easy", "stress free", "painless"]

for ctec in ctecs.find():
	ctec['easiness'] = sum([ctec['essay'].count(word) for word in easy_words])
	ctecs.save(ctec)
