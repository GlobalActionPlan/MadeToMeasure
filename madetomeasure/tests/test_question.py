import unittest

from pyramid import testing
from zope.interface.verify import verifyObject


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models import Question
        return Question()

    def test_title(self):
        obj = self._make_obj()
        self.assertEqual(obj.get_title(), u'')
        
        obj.set_title(u"Hello world")
        self.assertEqual(obj.get_title(), u"Hello world")

    def test_question_text(self):
        obj = self._make_obj()
        self.assertEqual(obj.get_question_text(), [])
        obj.set_question_text([{'lang':'somelang', 'text':"Very important text"}])
        self.assertEqual(obj.get_question_text(), [{'lang': 'somelang', 'text': 'Very important text'}])
        
    def test_schema_type(self):
        obj = self._make_obj()
        obj.set_question_type('Some type')
        self.assertEqual(obj.get_question_type(), "Some type")
        
    def test_get_schema(self):
        obj = self._make_obj()
        obj.set_question_type('FreeTextQuestion')
        obj.set_question_text([{'lang':'somelang', 'text':"Very important text"}])
        
        schema = obj.get_schema('somelang')
        #Answer is the field that will have the title of the actual question
        self.assertEqual(schema['answer'].title, "Very important text")
