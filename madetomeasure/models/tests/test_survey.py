# -*- coding: utf-8 -*-

import unittest
from datetime import datetime

import pytz
import colander
from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
from BTrees.OOBTree import OOBTree
from pyramid_mailer import get_mailer

from madetomeasure.models.exceptions import SurveyUnavailableError
from madetomeasure.interfaces import ISurvey


class SurveyTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models import Survey
        return Survey
    
    def _utcnow(self):
        from madetomeasure.models.date_time_helper import utcnow
        return utcnow()
    
    def _create_date(self, date_string):
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        return pytz.utc.localize(dt)
    
    def test_verify_class(self):
        self.failUnless(verifyClass(ISurvey, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(ISurvey, self._cut()))

    def test_welcome_text(self):
        obj = self._cut()
        value = "Let's start, mmmkey?"
        obj.set_welcome_text(value)
        self.assertEqual(obj.get_welcome_text(), value)
        value = 'Låt oss starta'
        obj.set_welcome_text(value, lang='sv')
        self.assertEqual(obj.get_welcome_text(lang='sv'), value)
    
    def test_finished_text(self):
        obj = self._cut()
        value = "We so happy now, okay?"
        obj.set_finished_text(value)
        self.assertEqual(obj.get_finished_text(), value)
        value = 'Vi är så glada nu'
        obj.set_finished_text(value, lang='sv')
        self.assertEqual(obj.get_finished_text(lang='sv'), value)

    def test_check_open_no_date_set(self):
        obj = self._cut()
        self.assertTrue(obj.check_open(), True)

    def test_check_open_start_time_passed(self):
        now = self._utcnow()
        obj = self._cut(start_time = now)
        self.assertEqual(obj.check_open(), True)

    def test_check_open_start_time_not_passed(self):
        future_date = self._create_date('2199-12-13')
        obj = self._cut(start_time = future_date)
        self.assertRaises(SurveyUnavailableError, obj.check_open)

    def test_check_open_end_time_passed(self):
        past_date = self._create_date('1999-12-13')
        obj = self._cut(end_time = past_date)
        self.assertRaises(SurveyUnavailableError, obj.check_open)
        
    def test_check_open_end_time_not_passed(self):
        future_date = self._create_date('2199-12-13')
        obj = self._cut(end_time = future_date)
        self.assertEqual(obj.check_open(), True)
        
    def test_untranslated_languages(self):
        self.config.scan('betahaus.pyracont.fields.password')
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
        
        from madetomeasure.models.surveys import Survey
        from madetomeasure.models import SurveySection
        s1 = Survey()
        s1.set_available_languages(['sv', 'de'])
        o1['surveys']['s1'] = s1

        ss1 = SurveySection()
        s1['ss1'] = ss1
        ss1.set_field_value('structured_question_ids', {'dummy': ['q1', 'q2']})
        
        langs = s1.untranslated_languages()
        self.assertEqual(len(langs.keys()), 2)
        self.assertEqual(len(langs['de']['questions']), 2)
        self.assertEqual(len(langs['sv']['questions']), 2)
        
        q1.set_question_text_lang('bla bla bla', 'sv')
        
        langs = s1.untranslated_languages()
        self.assertEqual(len(langs.keys()), 2)
        self.assertEqual(len(langs['de']['questions']), 2)
        self.assertEqual(len(langs['sv']['questions']), 1)
        
    def test_translations(self):
        obj = self._cut()
        self.assertEqual(len(obj.translations), 0)
        
        obj.set_translation('__welcome_text__', 'en', 'Welcome to the survey')
        
        self.assertTrue('__welcome_text__' in obj.translations)
        self.assertTrue('en' in obj.translations['__welcome_text__'])
        self.assertEqual(obj.translations['__welcome_text__']['en'], 'Welcome to the survey')
        self.assertEqual(obj.get_translation('__welcome_text__', 'en'), 'Welcome to the survey')
        
    def test_set_translated_titles(self):
        obj = self._cut()
        translations = {'en': 'h_en', 'sv': 'h_sv', 'dk': 'h_dk', }
        obj.set_heading_translations(translations)
        self.assertEqual(obj.field_storage['heading_translations'], translations)
        
    def test_get_translated_title(self):
        request = testing.DummyRequest(cookies={'_LOCALE_': 'sv'})
        self.config = testing.setUp(request=request)
        
        from madetomeasure.models.surveys import Surveys
        surveys = Surveys()
        
        obj = self._cut()
        surveys['s1'] = obj
        
        translations = {'en': 'h_en', 'sv': 'h_sv', 'dk': 'h_dk', }
        obj.set_heading_translations(translations)

        self.assertEqual(obj.get_translated_title(), 'h_sv')
        
    def test_create_ticket(self):
        obj = self._cut()
        ticket_uid = obj.create_ticket('test@test.com')
        self.assertTrue(ticket_uid in obj.tickets)
        
    def test_recreate_ticket(self):
        obj = self._cut()
        ticket_uid = obj.create_ticket('test@test.com')
        
        self.assertEqual(obj.create_ticket('test@test.com'), ticket_uid)
        
    def test_send_invitation_email(self):
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        self.config.include('pyramid_mailer.testing')

        obj = self._cut()

        obj.send_invitation_email(request, 'test@test.com', 'dumuid', 'Test')
        
        mailer = get_mailer(request)
        self.assertEqual(len(mailer.outbox), 1)
        
        msg = mailer.outbox[0]
        self.failUnless('dumuid' in msg.html)
    
    def test_start_survey(self):
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        
        from madetomeasure.models.root import SiteRoot
        root = SiteRoot()
        
        from madetomeasure.models.participants import Participants
        participants = Participants()
        root['participants'] = participants
        
        obj = self._cut()
        root['s1'] = obj
        
        ticket_uid = obj.create_ticket('test@test.com')
        request = testing.DummyRequest(params = {'uid':ticket_uid})
        self.config = testing.setUp(request=request)
        
        participant_uid = obj.start_survey(request)
        
        # participant is in sites participant list
        participant = participants.participant_by_ids(obj.__name__, participant_uid)
        self.assertIsNotNone(participants)
        
        # participant has the survey in its survey list
        self.assertTrue(obj.__name__ in participant.surveys)
        
    def test_get_participants_data(self):
        self.config.scan('betahaus.pyracont.fields.password')
        
        from madetomeasure.models.app import bootstrap_root
        root = bootstrap_root()
        
        from madetomeasure.models.questions import Question
        q1 = Question()
        q2 = Question()
        root['questions']['q1'] = q1
        root['questions']['q2'] = q2
        
        from madetomeasure.models.organisation import Organisation
        o1 = Organisation()
        root['questions']['o1'] = o1
        
        from madetomeasure.models.surveys import Survey
        from madetomeasure.models import SurveySection
        s1 = Survey()
        o1['surveys']['s1'] = s1

        ss1 = SurveySection()
        s1['ss1'] = ss1
        ss1.set_field_value('structured_question_ids', {'dummy': ['q1', 'q2']})
        
        s1.create_ticket('1@test.com')
        ticket_uid = s1.create_ticket('2@test.com')
        ss1.update_question_responses(ticket_uid, {'q1': 'dummy'})
        
        results = s1.get_participants_data()
        
        # two participants
        self.assertEqual(len(results), 2)
