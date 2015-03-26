from models import courses, ctecs

for course in courses.find({
		"school": "WCAS",
		"subject": "ECON",
		"catalog_num": "281-0",
		"instructor.name": {"$regex" : ".*Walker.*"}
}):

	print course['term'], course['instructor']['name']
	ctec = ctecs.find_one({"_id": course['_id']})
	if ctec:
		for statement in ctec['essay'].split("/"):
			print statement
	print "-------------------------"