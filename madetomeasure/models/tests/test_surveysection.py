import unittest

from pyramid import testing


class SurveyTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models import SurveySection
        return SurveySection()
    
    def test_reorder_questions(self):
        obj = self._make_obj()
        obj.set_structured_question_ids({'dummy1': ['q1', 'q2'], 'dummy2': ['q3']})
        
        obj.set_order(['q2', 'q3', 'q1'])
        self.assertEqual(obj.question_ids, ['q2', 'q3', 'q1'])
