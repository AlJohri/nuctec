from models import ctecs, courses
import csv

course_fieldnames = ["id", "term", "course_id", "class_num", "school", "subject", "catalog_num", "section", "title", "instructor", "start_time", "end_time", "meeting_days"]
ctec_fieldnames = ["enrollment_count", "response_count", "question0_average_rating", "question1_average_rating", "question2_average_rating", "question3_average_rating", "question4_average_rating", "easiness", "hardness", "essay"]
fieldnames = course_fieldnames + ctec_fieldnames

with open("ctecs.csv", "w") as f:
	writer = csv.DictWriter(f, fieldnames=fieldnames)
	writer.writeheader()
	for ctec in ctecs.find():
		course = courses.find_one({"_id": ctec["_id"]})
		course_ctec = dict(course)
		course_ctec.update(ctec)
		course_ctec['id'] = course_ctec.pop('_id')
		course_ctec['essay'] = course_ctec['essay'].encode('utf-8')
		writer.writerow({k:v for k,v in course_ctec.iteritems() if k in fieldnames})

		# print course_ctec['id'], course_ctec['term'], course_ctec['catalog_num'], course_ctec['instructor']