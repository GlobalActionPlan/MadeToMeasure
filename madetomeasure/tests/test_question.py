import unittest

import colander
from pyramid import testing
from zope.interface.verify import verifyObject
from BTrees.OOBTree import OOBTree

class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models import Question
        return Question()
    
    def _utils_fixture(self):
        from madetomeasure.models.question_types import register_question_node_utilities
        register_question_node_utilities(self.config)

    def _mock_text_question_data(self):
        data = OOBTree()
        data['dummy_question'] = [u"First answer", u"Second answer"]

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
        
    def test_question_type(self):
        obj = self._make_obj()
        self.assertEqual(obj.get_question_type(), "")
        obj.set_question_type('Some type')
        self.assertEqual(obj.get_question_type(), "Some type")

    def test_question_schema_node(self):
        self._utils_fixture()
        obj = self._make_obj()
        obj.set_question_type('free_text')
        node = obj.question_schema_node('dummy')
        self.assertTrue(isinstance(node, colander.SchemaNode))
    
    def test_render_result(self):
        self._utils_fixture()
        obj = self._make_obj()
        #FIXME: Use mock data