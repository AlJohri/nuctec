from models import ctecs, courses, terms

for ctec in ctecs.find({'corrected_essay': {'$exists': True}}):
	ctec['subj'] = ctec['subj'].split()[0]
	print unicode("[{academic_term}] - {subj} {class_title}").format(**ctec)
	print ctec['essay']
	print "-----------------------------"

# from utils import group_ctecs_by_course_id
# grouped_course_ctecs = group_ctecs_by_course_id()

# for course_id, course_ctecs in grouped_course_ctecs.iteritems():
# 	with open("temp/%s.txt" % course_id, "w") as f:
# 		for course_ctec in course_ctecs:
# 			f.write(course_ctec['title'])
# 			f.write("\n")
# 			f.write(course_ctec['essay'].encode('utf-8'))
# 			f.write("\n\n")
