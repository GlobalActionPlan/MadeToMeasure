import unittest
from datetime import datetime

import pytz
import colander
from pyramid import testing
from zope.interface.verify import verifyObject
from BTrees.OOBTree import OOBTree

from madetomeasure.models.exceptions import SurveyUnavailableError


class SurveyTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models import Survey
        return Survey()
    
    def _utcnow(self):
        from madetomeasure.models.date_time_helper import utcnow
        return utcnow()
    
    def _create_date(self, date_string):
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        return pytz.utc.localize(dt)
    
    def test_interface(self):
        from madetomeasure.interfaces import ISurvey
        obj = self._make_obj()
        self.assertTrue(verifyObject(ISurvey, obj))

    def test_from_address(self):
        obj = self._make_obj()
        email_field = "noreply@betahaus.net"
        obj.set_from_address(email_field)
        self.assertEqual(obj.get_from_address(), email_field)

    def test_welcome_text(self):
        obj = self._make_obj()
        value = "Let's start, mmmkey?"
        obj.set_welcome_text(value)
        self.assertEqual(obj.get_welcome_text(), value)
    
    def test_finished_text(self):
        obj = self._make_obj()
        value = "We so happy now, okay?"
        obj.set_finished_text(value)
        self.assertEqual(obj.get_finished_text(), value)

    def test_check_open_no_date_set(self):
        obj = self._make_obj()
        self.assertTrue(obj.check_open(), True)

    def test_check_open_start_time_passed(self):
        now = self._utcnow()
        obj = self._make_obj()
        obj.set_start_time(now)
        self.assertEqual(obj.check_open(), True)

    def test_check_open_start_time_not_passed(self):
        future_date = self._create_date('2199-12-13')
        obj = self._make_obj()
        obj.set_start_time(future_date)
        self.assertRaises(SurveyUnavailableError, obj.check_open)

    def test_check_open_end_time_passed(self):
        past_date = self._create_date('1999-12-13')
        obj = self._make_obj()
        obj.set_end_time(past_date)
        self.assertRaises(SurveyUnavailableError, obj.check_open)
        
    def test_check_open_end_time_not_passed(self):
        future_date = self._create_date('2199-12-13')
        obj = self._make_obj()
        obj.set_end_time(future_date)
        self.assertEqual(obj.check_open(), True)
        
    def test_untranslated_languages(self):
        from pyramid.interfaces import ISettings
        settings = self.config.registry.getUtility(ISettings)
        settings['default_locale_name'] = 'en'
        settings['available_languages'] = 'sv de'
        self.config.include('madetomeasure.models.translations')
        
        from madetomeasure.models.app import bootstrap_root
        self.root = bootstrap_root()
        
        from madetomeasure.models.questions import Question
        q1 = Question()
        q2 = Question()
        self.root['questions']['q1'] = q1
        self.root['questions']['q2'] = q2
        
        from madetomeasure.models.organisation import Organisation
        o1 = Organisation()
        self.root['questions']['o1'] = o1
        
        from madetomeasure.models.surveys import Survey, SurveySection
        s1 = Survey()
        s1.set_available_languages(['sv', 'de'])
        o1['surveys']['s1'] = s1

        ss1 = SurveySection()
        s1['ss1'] = ss1
        ss1.set_structured_question_ids({'dummy': ['q1', 'q2']})
        
        langs = s1.untranslated_languages()
        self.assertEqual(len(langs.keys()), 2)
        self.assertEqual(len(langs['de']['questions']), 2)
        self.assertEqual(len(langs['sv']['questions']), 2)
        
        q1.set_question_text_lang('bla bla bla', 'sv')
        
        langs = s1.untranslated_languages()
        self.assertEqual(len(langs.keys()), 2)
        self.assertEqual(len(langs['de']['questions']), 2)
        self.assertEqual(len(langs['sv']['questions']), 1)
