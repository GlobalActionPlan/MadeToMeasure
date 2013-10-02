import unittest

import colander
from deform.widget import TextInputWidget
from pyramid import testing
from zope.component import adapts
from zope.interface import implements
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from madetomeasure.interfaces import IQuestionType
from madetomeasure.interfaces import IQuestionTypes
from madetomeasure.interfaces import IQuestionWidget
from madetomeasure.interfaces import ITextQuestionType
from madetomeasure.interfaces import INumberQuestionType
from madetomeasure.interfaces import IChoiceQuestionType
from madetomeasure.interfaces import IMultiChoiceQuestionType


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

    def test_widget(self):
        self.config.registry.registerAdapter(_DummyWidgetAdapter, name = 'dummy')
        obj = self._cut(input_widget = 'dummy')
        self.assertIsInstance(obj.widget, _DummyWidgetAdapter)

    def test_widget_not_set(self):
        obj = self._cut(input_widget = 'other')
        self.assertEqual(obj.widget, None)

    def test_node_default_widget(self):
        obj = self._cut()
        result = obj.node('dummy')
        self.assertIsInstance(result, colander.SchemaNode)
        self.assertIsInstance(result.typ, colander.String)

    def test_node_widget_adapter_set(self):
        self.config.registry.registerAdapter(_DummyWidgetAdapter, name = 'dummy')
        obj = self._cut(input_widget = 'dummy')
        result = obj.node('dummy')
        self.assertIsInstance(result, colander.SchemaNode)
        self.assertIsInstance(result.widget, TextInputWidget)

    def test_default_kwargs_used(self):
        obj = self._cut()
        obj.default_kwargs = {'title': u'Hey'}
        result = obj.node('dummy')
        self.assertEqual(result.title, 'Hey')

    def test_node_kwargs_on_init_passed(self):
        obj = self._cut()
        result = obj.node('dummy', title="Hello", missing=u"", description="Test")
        self.assertEqual(result.title, "Hello")
        self.assertEqual(result.missing, u"")
        self.assertEqual(result.description, "Test")

    def test_node_kwargs_overrides_default_kwargs(self):
        obj = self._cut()
        obj.default_kwargs = {'title': 'default title', 'missing': u''}
        result = obj.node('dummy', title="Hello", description="Test")
        self.assertEqual(result.title, "Hello")
        self.assertEqual(result.missing, u"")
        self.assertEqual(result.description, "Test")

    def test_count_occurences(self):
        data = [1, 1, 2, 2, 3, 3, 3, 4]
        obj = self._cut()
        result = obj.count_occurences(data)
        self.assertEqual(set(result.keys()), set([1, 2, 3, 4]))
        self.assertEqual(result[1], 2)
        self.assertEqual(result[2], 2)
        self.assertEqual(result[3], 3)
        self.assertEqual(result[4], 1)

    def test_render_result(self):
        data = ['Jane Doe', 'Jane Doe', 'James Doe', 'John Doe']
        request = testing.DummyRequest()
        obj = self._cut()
        result = obj.render_result(request, data)
        self.assertIn('Jane Doe', result)
        self.assertIn('James Doe', result)

    def test_csv_header(self):
        obj = self._cut(title = u'Hello world!')
        self.assertEqual(obj.csv_header(), [u'Hello world!'])

    def test_csv_export(self):
        data = ['Jane Doe', 'Jane Doe', 'James Doe', 'John Doe']
        obj = self._cut()
        self.assertEqual(obj.csv_export(data), [['', 'Jane Doe'], ['', 'Jane Doe'], ['', 'James Doe'], ['', 'John Doe']])

    def test_csv_export_numberic(self):
        data = [1, 2, 3]
        obj = self._cut()
        self.assertEqual(obj.csv_export(data), [['', 1], ['', 2], ['', 3]])

    def test_check_safe_delete_nothing_set(self):
        root = _fixture(self.config)
        root['question_types']['qt1'] = obj = self._cut()
        request = testing.DummyRequest()
        self.assertEqual(obj.check_safe_delete(request), True)

    def test_check_safe_qt_set(self):
        root = _fixture(self.config)
        root['question_types']['qt1'] = obj = self._cut()
        root['questions']['q1'].set_question_type('qt1')
        request = testing.DummyRequest()
        self.assertEqual(obj.check_safe_delete(request), False)


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
        self.failUnless(verifyClass(ITextQuestionType, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(ITextQuestionType, self._cut(None)))


class NumberQuestionTypeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
    
    @property
    def _cut(self):
        from madetomeasure.models.question_types import NumberQuestionType
        return NumberQuestionType

    def test_verify_class(self):
        self.failUnless(verifyClass(INumberQuestionType, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(INumberQuestionType, self._cut(None)))

    def test_node_default_widget(self):
        obj = self._cut()
        result = obj.node('dummy')
        self.assertIsInstance(result, colander.SchemaNode)
        self.assertIsInstance(result.typ, colander.Decimal)


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
        self.failUnless(verifyClass(IChoiceQuestionType, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IChoiceQuestionType, self._cut(None)))


class MultiChoiceQuestionTypeTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
    
    @property
    def _cut(self):
        from madetomeasure.models.question_types import MultiChoiceQuestionType
        return MultiChoiceQuestionType

    def test_verify_class(self):
        self.failUnless(verifyClass(IMultiChoiceQuestionType, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IMultiChoiceQuestionType, self._cut(None)))

#FIXME: Once again, proper testing


class _DummyWidgetAdapter(object):
    name = u'dummy_widget'
    title = u'Dummy Widget'
    adapts(IQuestionType)
    implements(IQuestionWidget)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kw):
        return TextInputWidget()


def _fixture(config):
    from madetomeasure.models.app import bootstrap_root
    from madetomeasure.models.questions import Question
    config.scan('betahaus.pyracont.fields.password')
    root = bootstrap_root()
    root['questions']['q1'] = Question()
    root['questions']['q2'] = Question()
    return root
