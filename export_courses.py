from models import courses
import csv

course_fieldnames = ["id", "term", "year", "quarter", "course_id", "class_num", "school", "subject", "catalog_num", "section", "title", "instructor", "start_time", "end_time", "meeting_days"]
fieldnames = course_fieldnames

with open("courses.csv", "w") as f:
	writer = csv.DictWriter(f, fieldnames=fieldnames)
	writer.writeheader()
	for course in courses.find({"term": "2015 Spring"}):
		course = dict(course)
		course['id'] = course.pop('_id')
		course['year'] = course['term'].split()[0]
		course['quarter'] = course['term'].split()[1]
		course['instructor'] = course['instructor']['name']
		writer.writerow({k:v for k,v in course.iteritems() if k in fieldnames})