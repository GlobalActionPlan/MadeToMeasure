# -*- coding: utf-8 -*-
import unittest

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from madetomeasure.interfaces import ISurveySection


class SurveySectionTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.survey_section import SurveySection
        return SurveySection

    def _survey_fixture(self, survey_section, **kwargs):
        from madetomeasure.models.surveys import Survey
        survey = Survey(**kwargs)
        survey['section'] = survey_section
        return survey

    def test_verify_class(self):
        self.failUnless(verifyClass(ISurveySection, self._cut))

    def test_verify_obj(self):
        #title property causes object to call survey to fetch language stuff, hence more fixture is needed
        self.config = testing.setUp(request=testing.DummyRequest())
        obj = self._cut()
        self._survey_fixture(obj)
        self.failUnless(verifyObject(ISurveySection, obj))

    def test_reorder_questions(self):
        obj = self._cut()
        self._survey_fixture(obj)
        obj.set_field_value('structured_question_ids', {'dummy1': ['q1', 'q2'], 'dummy2': ['q3']})        
        obj.set_order(['q2', 'q3', 'q1'])
        self.assertEqual(obj.question_ids, ('q2', 'q3', 'q1'))
