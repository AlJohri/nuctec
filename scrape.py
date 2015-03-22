import os, sys, pickle, requests, lxml.html, logging
from models import careers, terms, schools, subjects, caesar_subjects, courses, ctecs

asg_api_key = os.getenv('ASG_API_KEY')
netid = os.getenv('NETID')
password = os.getenv('PASSWORD')

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

# filename='scrape.log',

class DescriptionsScraper(object):

    API_URL = "http://www.northwestern.edu/class-descriptions/"

    def get_terms(self): return self.get(API_URL)
    def get_schools(self, term): return self.get(API_URL + "/%s/" % term)
    def get_subjects(self, term, school): return self.get(API_URL + "/%s/%s/" % (term, school))
    def get_courses(self, term, school, subject): return self.get(API_URL + "/%s/%s/%s/" % (term, school, subject))
    def get_descriptions(self, term, school, subject, course): return self.get(API_URL + "/%s/%s/%s/%s/" % (term, school, subject, course))

    def get(self, path, **kwargs):
        return requests.get(path + "index-v2.json", **kwargs).json()

class ASGScraper(object):

    API_URL = "http://api.asg.northwestern.edu/%s"

    def __init__(self):
        self.params = {'key' : asg_api_key}

    def get_terms(self): return self.get("terms")
    def get_schools(self): return self.get("schools")
    def get_subjects(self, term=None, school=None):
        return self.get("subjects", params={"term": term, "school": school})
    def get_courses(self, subject, term):
        return self.get("courses/details", params={"term": term, "subject": subject})

    def get(self, endpoint, **kwargs):
        kwargs['params'] = kwargs.get('params', {})
        kwargs['params'].update(self.params)
        kwargs['params'] = { k: v for k, v in kwargs['params'].items() if v is not None }
        return requests.get(self.API_URL % endpoint, **kwargs).json()

class CaesarScraper(object):

    LOGIN_URL = "https://ses.ent.northwestern.edu/psp/s9prod/?cmd=login&languageCd=ENG"
    CTEC_URL = "https://ses.ent.northwestern.edu/psc/caesar/EMPLOYEE/HRMS/c/NWCT.NW_CT_PUBLIC_VIEW.GBL"
    COURSE_URL = "https://ses.ent.northwestern.edu/psc/caesar/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL"

    NO_LONGER_AVAILABLE_CAESAR_PAGE = "This page is no longer available."
    BLANK_CAESAR_PAGE = "meta HTTP-EQUIV='Refresh'"

    __attrs__ = ['session', 'icsid', 'icelementnum', 'icstatenum']

    def __init__(self):
        self.session = requests.Session()
        self.post(self.LOGIN_URL, data={"userid": netid, "pwd": password})
        doc = lxml.html.fromstring(self.post(self.CTEC_URL).content)
        self.set_ic_values(doc)

    def reset(self):
        response = self.post(self.CTEC_URL, data={"ICAction": ""})
        doc = lxml.html.fromstring(response.content)
        self.set_ic_values(doc)

    def payload(self):
        return {
            "ICSID": self.icsid,
            "ICElementNum": self.icelementnum,
            "ICStateNum": self.icstatenum
        }

    def __getstate__(self):
        return dict((attr, getattr(self, attr, None)) for attr in self.__attrs__)

    def __setstate__(self, state):
        for attr, value in state.items():
            setattr(self, attr, value)

    def set_ic_values(self, doc):
        self.icsid = doc.cssselect("#ICSID")[0].get('value')
        self.icelementnum = doc.cssselect("#ICElementNum")[0].get('value')
        self.icstatenum = doc.cssselect("#ICStateNum")[0].get('value')

    def get_doc(self, url, **kwargs):
        kwargs['data'] = kwargs.get('data', {})
        kwargs['data'].update(self.payload())
        response = self.session.get(url, **kwargs)
        self.last_response = response
        if self.BLANK_CAESAR_PAGE in response.content: raise Exception("CAESAR Session Expired")
        if self.NO_LONGER_AVAILABLE_CAESAR_PAGE in response.content:
            raise Exception("This page is no longer available." +
                "To continue, return to your most recent active page " +
                "or select one of the navigation icons in the header above.")
        doc = lxml.html.fromstring(response.content)
        self.set_ic_values(doc)
        return doc

    def post_doc(self, url, **kwargs):
        kwargs['data'] = kwargs.get('data', {})
        kwargs['data'].update(self.payload())
        response = self.session.post(url, **kwargs)
        self.last_response = response
        if self.BLANK_CAESAR_PAGE in response.content: raise Exception("CAESAR Session Expired")
        if self.NO_LONGER_AVAILABLE_CAESAR_PAGE in response.content:
            raise Exception("This page is no longer available." +
                "To continue, return to your most recent active page " +
                "or select one of the navigation icons in the header above.")
        doc = lxml.html.fromstring(response.content)
        self.set_ic_values(doc)
        return doc

    def get(self, url, **kwargs): return self.session.get(url, **kwargs)
    def post(self, url, **kwargs): return self.session.post(url, **kwargs)

    def write_doc(self, doc):
        with open("test.html", "w") as f:
            f.write(lxml.html.tostring(doc))

    def write_last_response(self):
        with open("test.html", "w") as f:
            f.write(self.last_response.content)

    def get_careers(self):
        doc = self.get_doc(self.CTEC_URL)
        return [{'symbol': option.get('value'), 'name':option.text} for option in doc.cssselect("#NW_CT_PB_SRCH_ACAD_CAREER option") if not option.get('selected')]

    def get_subjects(self, career="UGRD"):
        doc = self.post_doc(self.CTEC_URL, data={"ICAction": "NW_CT_PB_SRCH_ACAD_CAREER", "NW_CT_PB_SRCH_ACAD_CAREER": career})
        return [{'symbol': option.get('value'), 'name':option.text, 'career': career} for option in doc.cssselect("#NW_CT_PB_SRCH_SUBJECT option") if not option.get('selected')]

    def get_courses(self, subject, career="UGRD"):
        doc = self.post_doc(self.CTEC_URL, data={"ICAction": "NW_CT_PB_SRCH_SRCH_BTN", "NW_CT_PB_SRCH_ACAD_CAREER": career, "NW_CT_PB_SRCH_SUBJECT": subject, "NW_CT_PB_SRCH_NW_CTEC_SRCH_CHOIC$4$": "C"})
        return [(
            int(x.cssselect('span.PSHYPERLINK a')[0].get('id').split("$")[-1]),
            x.cssselect('span.PSEDITBOX_DISPONLY')[0].text
        ) for x in doc.cssselect("#NW_CT_PV_DRV\$scroll\$0 tr[id*=tr]")]

    def get_ctecs(self, subject, index, career="UGRD"):
        doc = self.post_doc(self.CTEC_URL, data={"ICAction": "MYLINK$%d" % index, "NW_CT_PB_SRCH_ACAD_CAREER": career, "NW_CT_PB_SRCH_SUBJECT": subject, "NW_CT_PB_SRCH_NW_CTEC_SRCH_CHOIC$4$": "C"})
        return [(
            int(x.cssselect('span.PSHYPERLINK a')[0].get('id').split("$")[-1]),
            x.cssselect('span.PSEDITBOX_DISPONLY:nth-child(1)')[0].text
        ) for x in doc.cssselect("#NW_CT_PV4_DRV\$scroll\$0 tr[id*=tr]")]

    def get_ctec(self, subject, index, career="UGRD"):
        doc = self.post_doc(self.CTEC_URL, data={"ICAction": "MYLINK1$%d" % index, "NW_CT_PB_SRCH_ACAD_CAREER": career, "NW_CT_PB_SRCH_SUBJECT": subject, "NW_CT_PB_SRCH_NW_CTEC_SRCH_CHOIC$4$": "C"})

        if "While fetching the value of an array element" in self.last_response.content:
            self.post_doc(self.CTEC_URL, data={"ICAction" : "NW_CT_PV_NAME_RETURN_PB"})
            return {}

        # NW_CTEC_P_SEARCH, NW_CTEC_P_EVALUATI
        if doc.cssselect("#pt_pageinfo_win0")[0].get('page') == 'NW_CTEC_P_SEARCH':
            self.post_doc(self.CTEC_URL, data={"ICAction" : "NW_CT_PV_NAME_RETURN_PB"})
            raise Exception("it went back to the search page while trying to get a ctec")

        essay_prompt1 = "\r\nPlease summarize your reaction to this course focusing on the aspects that were most important to you.\r\n"
        essay_prompt2 = "\n\nEssay Questions\r\n\r\n"

        essay = doc.cssselect("#win0divNW_CT_PV3_DRV_DESCRLONG\$0")[0].text_content().replace(essay_prompt1, "").replace(essay_prompt2, "") if doc.cssselect("#win0divNW_CT_PV3_DRV_DESCRLONG\$0") else ""
        academic_term = doc.cssselect("#NW_CT_DERIVED_0_NW_CT_TERM_DESCR")[0].text_content()
        subj = doc.cssselect("#NW_CT_DERIVED_0_NW_CT_DEPARTMENT")[0].text_content()
        class_title = doc.cssselect("#NW_CT_DERIVED_0_NW_CT_COURSE")[0].text_content()
        instructor = doc.cssselect("#NW_CT_PV_NAME_NAME")[0].text_content()
        enrollment_count = doc.cssselect("#NW_CT_DERIVED_0_NW_CT_ENROLLCOUNT")[0].text_content()
        response_count = doc.cssselect("#NW_CT_DERIVED_0_NW_CT_RESPONSECNT")[0].text_content()

        question0_response_count = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$0 > div > div > table > tr:nth-child(1) > td:nth-child(2) > font")[0].text
        question1_response_count = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$1 > div > div > table > tr:nth-child(1) > td:nth-child(2) > font")[0].text
        question2_response_count = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$2 > div > div > table > tr:nth-child(1) > td:nth-child(2) > font")[0].text
        question3_response_count = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$3 > div > div > table > tr:nth-child(1) > td:nth-child(2) > font")[0].text
        question4_response_count = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$4 > div > div > table > tr:nth-child(1) > td:nth-child(2) > font")[0].text
        try:
            question5_response_count = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$5 > div > table > tr > td:nth-child(2) > font")[0].text
        except:
            question5_response_count = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$5 > div > div > table > tr:nth-child(1) > td:nth-child(2) > font")[0].text

        question0_average_rating = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$0 > div > div > table > tr:nth-child(1) > td:nth-child(1) > div > div")[0].text if question0_response_count else ""
        question1_average_rating = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$1 > div > div > table > tr:nth-child(1) > td:nth-child(1) > div > div")[0].text if question1_response_count else ""
        question2_average_rating = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$2 > div > div > table > tr:nth-child(1) > td:nth-child(1) > div > div")[0].text if question2_response_count else ""
        question3_average_rating = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$3 > div > div > table > tr:nth-child(1) > td:nth-child(1) > div > div")[0].text if question3_response_count else ""
        question4_average_rating = doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$4 > div > div > table > tr:nth-child(1) > td:nth-child(1) > div > div")[0].text if question4_response_count else ""
        # time-spent question has no average rating

        question0_histogram = [x.text for x in doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$0 > div > div > table > tr:nth-child(2) > td > div:nth-child(2) > div")]
        question1_histogram = [x.text for x in doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$1 > div > div > table > tr:nth-child(2) > td > div:nth-child(2) > div")]
        question2_histogram = [x.text for x in doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$2 > div > div > table > tr:nth-child(2) > td > div:nth-child(2) > div")]
        question3_histogram = [x.text for x in doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$3 > div > div > table > tr:nth-child(2) > td > div:nth-child(2) > div")]
        question4_histogram = [x.text for x in doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$4 > div > div > table > tr:nth-child(2) > td > div:nth-child(2) > div")]
        question5_histogram = [x.text for x in doc.cssselect("#win0divNW_CT_PV2_DRV_DESCRLONG\$5 > div > table > tr > td:nth-child(1) > div > div:nth-child(2) > div")]

        ctec = {
            "essay": essay,
            "academic_term": academic_term,
            "subj": subj,
            "class_title": class_title,
            "instructor": instructor,
            "enrollment_count": enrollment_count,
            "response_count": response_count,
            "question0_response_count": question0_response_count,
            "question1_response_count": question1_response_count,
            "question2_response_count": question2_response_count,
            "question3_response_count": question3_response_count,
            "question4_response_count": question4_response_count,
            "question5_response_count": question5_response_count,
            "question0_average_rating": question0_average_rating,
            "question1_average_rating": question1_average_rating,
            "question2_average_rating": question2_average_rating,
            "question3_average_rating": question3_average_rating,
            "question4_average_rating": question4_average_rating,
            "question0_histogram": question0_histogram,
            "question1_histogram": question1_histogram,
            "question2_histogram": question2_histogram,
            "question3_histogram": question3_histogram,
            "question4_histogram": question4_histogram,
            "question5_histogram": question5_histogram
        }

        self.post_doc(self.CTEC_URL, data={"ICAction" : "NW_CT_PV_NAME_RETURN_PB"})

        return ctec

    # @staticmethod
    # def load():
    #     if not os.path.isfile('caesar_session.pickle'):
    #         caesar_scraper = CaesarScraper()
    #         # pickle.dump(caesar_scraper, open('caesar_session.pickle', 'wb'))
    #     else:
    #         caesar_scraper = pickle.load(open('caesar_session.pickle', "rb" ))
    #         caesar_scraper.reset()
    #     return caesar_scraper


def get_all_ctecs(subject, caesar_scraper=None):
    logging.debug('Starting %s' % subject)
    caesar_scraper = caesar_scraper or CaesarScraper()
    for i, current_class_title in caesar_scraper.get_courses(subject):
        logging.debug("Starting %s %s %s" % (subject, current_class_title, i))
        for j, quarter in caesar_scraper.get_ctecs(subject, i):
            ctec = caesar_scraper.get_ctec(subject, j)
            if ctec == {}: continue

            current_catalog_num = current_class_title.split(":")[0]
            original_catalog_num = "-".join(ctec['class_title'].split()[0].split("-")[0:2])

            ctec['current_class_title'] = current_class_title

            section = ctec['class_title'].split()[0].split("-")[2]
            subj = ctec['subj'].split()[0]
            courses_query = courses.find({"term": quarter, "catalog_num": original_catalog_num, "subject": subj, "section": section})

            if courses_query.count() > 1:
                courses_query = courses.find({"term": quarter, "catalog_num": original_catalog_num, "subject": subj, "section": section, "instructor.name": {"$regex" : ".*".join(ctec['instructor'].split())}})
                if courses_query.count() > 1:
                    logging.error("%s too many courses found for %s %s %s %s %s" % (j, quarter, original_catalog_num, subj, section, ctec['instructor']))
                elif courses_query.count() == 1:
                    logging.error("%s no courses found for %s %s %s %s %s" % (j, quarter, original_catalog_num, subj, section, ctec['instructor']))
            elif courses_query.count() == 0:
                logging.error("%s no courses found for %s %s %s %s" % (j, quarter, original_catalog_num, subj, section))

            if courses_query.count() == 1:
                course = list(courses_query)[0]
                ctec['_id'] = course['_id']
                ctecs.save(ctec)
                logging.debug("Saved %s %s %s %s %s" % (subject, current_catalog_num, quarter, i, j))

            # BUG, if the course starts with 300, CTEC thinks its part of the graduate school
            if original_catalog_num[0] == "3" or subj != subject:
                caesar_scraper.post_doc(caesar_scraper.CTEC_URL, data={"ICAction": "NW_CT_PB_SRCH_ACAD_CAREER", "NW_CT_PB_SRCH_ACAD_CAREER": "UGRD", "NW_CT_PB_SRCH_SUBJECT": subject, "NW_CT_PB_SRCH_NW_CTEC_SRCH_CHOIC$4$": "C"})
                caesar_scraper.post_doc(caesar_scraper.CTEC_URL, data={"ICAction": "NW_CT_PB_SRCH_SUBJECT", "NW_CT_PB_SRCH_ACAD_CAREER": "UGRD", "NW_CT_PB_SRCH_SUBJECT": subject, "NW_CT_PB_SRCH_NW_CTEC_SRCH_CHOIC$4$": "C"})
                caesar_scraper.get_courses(subject)
                caesar_scraper.get_ctecs(subject, i)
            elif subj == "AAL" or subj == "AF_AM_ST":
                caesar_scraper.get_ctecs(subject, i)
                # sometimes after getting a single ctec, we need to get ctecs again
                # because it routes back to the list of courses page

        caesar_scraper.get_courses(subject)
        # after getting all the ctecs for a single course, we need to get_courses again
    logging.debug('Finished %s' % subject)

if __name__ == '__main__':

    if not asg_api_key or not netid or not password:
        raise Exception("Please source the .secret file.")

    if len(sys.argv) != 2:
        raise Exception("Please provide subject. Example Usage: python scrape.py EECS")

    caesar_scraper = CaesarScraper()
    asg_scraper = ASGScraper()

    if careers.count() == 0:
        print "Scraping careers... "
        careers.insert([{'_id': career['symbol'], 'name': career['name']} for career in caesar_scraper.get_careers()])

    if schools.count() == 0:
        print "Scraping schools... "
        schools.insert([{'_id': school['symbol'], 'name': school['name']} for school in asg_scraper.get_schools()])

    if terms.count() == 0:
        print "Scraping terms... "
        terms.insert([{'_id': term['id'], 'name': term['name'], 'start_date': term['start_date'], 'end_date': term['end_date']} for term in asg_scraper.get_terms()])

    if subjects.count() == 0:
        for term in terms.find():
            for school in schools.find():
                print "Scraping subjects for %s %s... " % (term['_id'], school['_id'])
                data = [{'term':term['_id'], 'school':school['_id'], 'symbol': subject['symbol'], 'name': subject['name']} for subject in asg_scraper.get_subjects(term=term['_id'], school=school['_id'])]
                if not data: continue
                subjects.insert(data) # prevents "pymongo.errors.InvalidOperation: cannot do an empty bulk write"

    if caesar_subjects.count() == 0:
        caesar_subjects.insert([{'_id': subject['symbol'], 'name': subject['name'], 'career': subject['career']} for subject in caesar_scraper.get_subjects("UGRD")])

    if courses.count() == 0:
        for term in terms.find():
            for school in schools.find():
                for subject in subjects.find({"term": term['_id'], "school": school['_id']}):
                    print "Scraping courses for %s %s %s... " % (term['_id'], school['_id'], subject['symbol'])
                    courses_raw = asg_scraper.get_courses(subject['symbol'], term['_id'])
                    for course in courses_raw:
                        course['_id'] = course.pop('id')
                    if not courses_raw: continue
                    for course in courses_raw:
                        courses.save(course)

    subject = sys.argv[1]
    get_all_ctecs(subject, caesar_scraper)
