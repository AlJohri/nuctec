import logging

from Queue import Queue
from threading import Thread

from models import caesar_subjects
from scrape import get_all_ctecs

def worker():
    while True:
        subject = q.get()
        cs = caesar_subjects.find_one({"_id": subject})
        try:
            get_all_ctecs(subject)
            cs['scraped'] = True
        except Exception as e:
            logging.debug(e)
            cs['error'] = True

        caesar_subjects.save(cs)
        q.task_done()

q = Queue()
for i in range(5):
     t = Thread(target=worker)
     t.daemon = True
     t.start()

for subject in caesar_subjects.find({"scraped": {'$exists': False}}):
    q.put(subject['_id'])

q.join()