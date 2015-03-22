import threading

from models import caesar_subjects
from scrape import get_all_ctecs

subjects = [x for x in caesar_subjects.find()]

threads = []
for subject in subjects:
    t = threading.Thread(name=subject['_id'], target=get_all_ctecs, args=(subject['_id'],))
    threads.append(t)
    t.start()