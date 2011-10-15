# -*- coding: utf-8 -*-

import unittest

import colander
from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject
from BTrees.OOBTree import OOBTree


class QuestionTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models import Question
        return Question
    
    def _utils_fixture(self):
        self.config.include('madetomeasure.models.question_types')

    def test_interface(self):
        from madetomeasure.interfaces import IQuestion
        obj = self._cut()
        self.assertTrue(verifyObject(IQuestion, obj))

    def test_question_text(self):
        obj = self._cut()
        self.assertEqual(len(obj.get_question_text()), 0)
        obj.set_question_text({'sv':'Hej hej'})
        self.assertEqual(obj.get_question_text(), {'sv':'Hej hej'})
        obj.set_question_text_lang('Hello world', 'en')
        self.assertEqual(obj.get_question_text(), {'sv':'Hej hej', 'en': 'Hello world'})
        
    def test_question_text_empty_value(self):
        obj = self._cut()
        obj.set_question_text({'sv':'Hej hej', 'other':''})
        self.assertEqual(obj.get_question_text(), {'sv':'Hej hej'})
        obj.set_question_text_lang('', 'other')
        self.assertEqual(obj.get_question_text(), {'sv':'Hej hej'})

    def test_question_type(self):
        obj = self._cut()
        self.assertEqual(obj.get_question_type(), "")
        obj.set_question_type('Some type')
        self.assertEqual(obj.get_question_type(), "Some type")

    def test_question_schema_node(self):
        self._utils_fixture()
        obj = self._cut()
        obj.set_question_type('importance_scale')
        node = obj.question_schema_node('dummy')
        self.assertTrue(isinstance(node, colander.SchemaNode))
    
    def test_render_result(self):
        self._utils_fixture()
        obj = self._cut()
        obj.set_question_type('free_text')
        
        request = testing.DummyRequest()
        data = ['I wrote something', "She wrote something else"]
        
        result = obj.render_result(request, data)
        self.assertTrue('I wrote something' in result)
        
    def test_question_variant(self):
        request = testing.DummyRequest()
        self.config = testing.setUp(request=request)
        
        from madetomeasure.interfaces import IQuestionTranslations
        from madetomeasure.models.translations import QuestionTranslations
        settings = dict(default_locale_name='en',
                        available_languages='en sv de ru',)
        trans_util = QuestionTranslations(settings)
        self.config.registry.registerUtility(trans_util, IQuestionTranslations)
        
        from madetomeasure.models.organisation import Organisation
        org = Organisation()

        obj = self._cut(title = "Hello world")

        self.assertEqual(obj.get_title(), u"Hello world")
        self.assertEqual(obj.get_title(lang='en'), u"Hello world")
        self.assertEqual(obj.get_title(lang='sv'), u"Hello world")

        org.set_variant(obj.__name__, 'sv', u'Hej världen')
        self.assertNotEqual(obj.get_title(lang='sv', context=org), u"Hello world")
        self.assertEqual(obj.get_title(lang='sv', context=org), u"Hej världen")
        
        org.set_variant(obj.__name__, 'en', u'Gday world')
        self.assertNotEqual(obj.get_title(context=org), u"Hello world")
        self.assertEqual(obj.get_title(context=org), u"Gday world")
