import unittest

from pyramid import testing


class SelectLanguageTests(unittest.TestCase):
    """ This refers to app.py - select_language """
    
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _fut(self):
        from madetomeasure.models.app import select_language
        return select_language

    def _survey(self):
        from madetomeasure.models import Survey
        return Survey()

    def test_survey_one_lang(self):
        survey = self._survey()
        available_langs = set(['en'])
        survey.set_available_languages(available_langs)

        self.assertEqual(self._fut(survey), 'en')
    
    def test_no_lang_set(self):
        survey = self._survey()
        request = testing.DummyRequest()
        self.assertEqual(self._fut(survey, request), None)

    def test_several_langs_no_session_set(self):
        survey = self._survey()
        request = testing.DummyRequest()

        available_langs = set(['en', 'sv'])
        survey.set_available_languages(available_langs)

        self.assertEqual(self._fut(survey, request), None)

    def test_lang_set_in_session(self):
        survey = self._survey()
        available_langs = set(['en', 'sv'])
        survey.set_available_languages(available_langs)

        request = testing.DummyRequest()
        request.session['lang'] = 'sv'

        self.assertEqual(self._fut(survey, request), 'sv')
