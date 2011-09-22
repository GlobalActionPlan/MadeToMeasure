import unittest

import colander
from pyramid import testing
from zope.interface.verify import verifyObject

from madetomeasure.interfaces import IQuestionNode


class BasicQuestionNodeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.question_types import BasicQuestionNode
        from madetomeasure.models.question_types import text_area_widget
        return BasicQuestionNode('test_node', text_area_widget)

    def test_interface(self):
        obj = self._make_obj()
        self.failUnless(verifyObject(IQuestionNode, obj))

    def test_node(self):
        obj = self._make_obj()
        node = obj.node('node_name')
        self.failUnless(isinstance(node, colander.SchemaNode))
        from madetomeasure.models.question_types import text_area_widget
        self.assertEqual(node.widget, text_area_widget)
    
    def test_count_occurences(self):
        obj = self._make_obj()
        data = ('one', 'one', 'one', 'two', 'three')
        results = obj.count_occurences(data)
        self.assertEqual(results['one'], 3)
        self.assertEqual(set(results), set(data))
    
    def test_render_result(self):
        obj = self._make_obj()
        data = ('one', 'one', 'one', 'two', 'three')
        request = testing.DummyRequest()
        result = obj.render_result(request, data)
        self.failUnless('three' in result)

    def test_kwargs_on_init_passed_to_node(self):
        from madetomeasure.models.question_types import BasicQuestionNode
        from madetomeasure.models.question_types import text_area_widget
        obj = BasicQuestionNode('test_node', text_area_widget, title="Hello", missing=u"", description="Test")
        node = obj.node('test_node')
        self.assertEqual(node.title, "Hello")
        self.assertEqual(node.missing, u"")
        self.assertEqual(node.description, "Test")

    def test_node_kwargs_overrides_default_kwargs(self):
        from madetomeasure.models.question_types import BasicQuestionNode
        from madetomeasure.models.question_types import text_area_widget
        obj = BasicQuestionNode('test_node', text_area_widget, title="Hello")
        node = obj.node('test_node', title="Goodbye!")
        self.assertEqual(node.title, "Goodbye!")


class ChoiceQuestionNodeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.question_types import ChoiceQuestionNode
        from madetomeasure.models.question_types import importance_choices_widget
        return ChoiceQuestionNode('test_node', importance_choices_widget)

    def test_interface(self):
        obj = self._make_obj()
        self.failUnless(verifyObject(IQuestionNode, obj))

    def test_node(self):
        obj = self._make_obj()
        node = obj.node('node_name')
        self.failUnless(isinstance(node, colander.SchemaNode))
        from madetomeasure.models.question_types import importance_choices_widget
        self.assertEqual(node.widget, importance_choices_widget)
    
    def test_count_occurences(self):
        obj = self._make_obj()
        data = ('one', 'one', 'one', 'two', 'three')
        results = obj.count_occurences(data)
        self.assertEqual(results['one'], 3)
        self.assertEqual(set(results), set(data))
    
    def test_render_result(self):
        obj = self._make_obj()
        #Data choices must be the same as the alternatives in the widget
        data = ('1', '3', '3', '4', '5')
        request = testing.DummyRequest()
        result = obj.render_result(request, data)
        self.failUnless('1 - Not important' in result)

    def test_choice_values(self):
        obj = self._make_obj()
        results = obj.choice_values()
        choices = set([str(x) for x in range(1, 8)])
        self.assertEqual(set(results.keys()), choices)


class QuestionNodeTests(unittest.TestCase):
    """ Generic stuff + integration """
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('madetomeasure.models.question_types')
        self.qu = self.config.registry.queryUtility

    def tearDown(self):
        testing.tearDown()
    
    def test_free_text_registered(self):
        self.failUnless(self.qu(IQuestionNode, name='free_text'))

    def test_importance_scale_registered(self):
        self.failUnless(self.qu(IQuestionNode, name='importance_scale'))
        
    def test_frequency_scale_registered(self):
        self.failUnless(self.qu(IQuestionNode, name='frequency_scale'))

    def test_yes_no_registered(self):
        self.failUnless(self.qu(IQuestionNode, name='yes_no'))
