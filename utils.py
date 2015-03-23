from collections import defaultdict
from models import ctecs, courses

def group_ctecs_by_course_id():
	grouped_course_ctecs = defaultdict(list)
	for ctec in ctecs.find():
		course = courses.find_one({"_id": ctec["_id"]})
		course_ctec = dict(course)
		course_ctec.update(ctec)
		course_ctec['id'] = course_ctec.pop('_id')
		key = str(course_ctec['course_id'])
		grouped_course_ctecs[key].append(course_ctec)
	return grouped_course_ctecs