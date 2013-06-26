import unittest

import colander
from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from madetomeasure.interfaces import IQuestionType
from madetomeasure.interfaces import IQuestionTypes
from madetomeasure.interfaces import ITextQuestionType
from madetomeasure.interfaces import IChoiceQuestionType


class QuestionTypesTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.question_types import QuestionTypes
        return QuestionTypes

    def test_verify_class(self):
        self.failUnless(verifyClass(IQuestionTypes, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IQuestionTypes, self._cut(None)))


class BaseQuestionTypeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.question_types import BaseQuestionType
        return BaseQuestionType

    def test_verify_class(self):
        self.failUnless(verifyClass(IQuestionType, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IQuestionType, self._cut(None)))


class TextQuestionTypeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.question_types import TextQuestionType
        return TextQuestionType

    def test_verify_class(self):
        self.failUnless(verifyClass(IQuestionType, self._cut))
        self.failUnless(verifyClass(ITextQuestionType, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IQuestionType, self._cut(None)))
        self.failUnless(verifyObject(ITextQuestionType, self._cut(None)))

#FIXME: Proper testing
#     def test_node(self):
#         obj = self._make_obj()
#         node = obj.node('node_name')
#         self.failUnless(isinstance(node, colander.SchemaNode))
#         from madetomeasure.models.question_types import text_area_widget
#         self.assertEqual(node.widget, text_area_widget)
#     
#     def test_count_occurences(self):
#         obj = self._make_obj()
#         data = ('one', 'one', 'one', 'two', 'three')
#         results = obj.count_occurences(data)
#         self.assertEqual(results['one'], 3)
#         self.assertEqual(set(results), set(data))
#     
#     def test_render_result(self):
#         obj = self._make_obj()
#         data = ('one', 'one', 'one', 'two', 'three')
#         request = testing.DummyRequest()
#         result = obj.render_result(request, data)
#         self.failUnless('three' in result)
# 
#     def test_kwargs_on_init_passed_to_node(self):
#         from madetomeasure.models.question_types import BasicQuestionNode
#         from madetomeasure.models.question_types import text_area_widget
#         obj = BasicQuestionNode('test_node', text_area_widget, title="Hello", missing=u"", description="Test")
#         node = obj.node('test_node')
#         self.assertEqual(node.title, "Hello")
#         self.assertEqual(node.missing, u"")
#         self.assertEqual(node.description, "Test")
# 
#     def test_node_kwargs_overrides_default_kwargs(self):
#         from madetomeasure.models.question_types import BasicQuestionNode
#         from madetomeasure.models.question_types import text_area_widget
#         obj = BasicQuestionNode('test_node', text_area_widget, title="Hello")
#         node = obj.node('test_node', title="Goodbye!")
#         self.assertEqual(node.title, "Goodbye!")


class ChoiceQuestionTypeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
    
    @property
    def _cut(self):
        from madetomeasure.models.question_types import ChoiceQuestionType
        return ChoiceQuestionType

    def test_verify_class(self):
        self.failUnless(verifyClass(IQuestionType, self._cut))
        self.failUnless(verifyClass(IChoiceQuestionType, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IQuestionType, self._cut(None)))
        self.failUnless(verifyObject(IChoiceQuestionType, self._cut(None)))
# 
#     def test_node(self):
#         obj = self._make_obj()
#         node = obj.node('node_name')
#         self.failUnless(isinstance(node, colander.SchemaNode))
#         from madetomeasure.models.question_types import importance_choices_widget
#         self.assertEqual(node.widget, importance_choices_widget)
#     
#     def test_count_occurences(self):
#         obj = self._make_obj()
#         data = ('one', 'one', 'one', 'two', 'three')
#         results = obj.count_occurences(data)
#         self.assertEqual(results['one'], 3)
#         self.assertEqual(set(results), set(data))
#     
#     def test_render_result(self):
#         obj = self._make_obj()
#         #Data choices must be the same as the alternatives in the widget
#         data = ('1', '3', '3', '4', '5')
#         request = testing.DummyRequest()
#         result = obj.render_result(request, data)
#         self.failUnless('1 - Not important' in result)
# 
#     def test_choice_values(self):
#         obj = self._make_obj()
#         results = obj.choice_values()
#         choices = set([str(x) for x in range(1, 8)])
#         self.assertEqual(set(results.keys()), choices)


# class QuestionNodeTests(unittest.TestCase):
#     """ Generic stuff + integration """
#     def setUp(self):
#         self.config = testing.setUp()
#         self.config.include('madetomeasure.models.question_types')
#         self.qu = self.config.registry.queryUtility
# 
#     def tearDown(self):
#         testing.tearDown()
#     
#     def test_free_text_registered(self):
#         self.failUnless(self.qu(IQuestionNode, name='free_text'))
# 
#     def test_importance_scale_registered(self):
#         self.failUnless(self.qu(IQuestionNode, name='importance_scale'))
#         
#     def test_frequency_scale_registered(self):
#         self.failUnless(self.qu(IQuestionNode, name='frequency_scale'))
# 
#     def test_yes_no_registered(self):
#         self.failUnless(self.qu(IQuestionNode, name='yes_no'))
