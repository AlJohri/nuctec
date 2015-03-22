from pymongo import MongoClient
client = MongoClient()
db = client.nuctec
careers = db.careers
terms = db.terms
schools = db.schools
subjects = db.subjects
caesar_subjects = db.caesar_subjects
courses = db.courses
instructors = db.instructors
buildings = db.buildings
rooms = db.rooms
ctecs = db.ctecs

subjects.ensure_index([("symbol", 1), ("term", 1), ("school", 1)], unique=True)
