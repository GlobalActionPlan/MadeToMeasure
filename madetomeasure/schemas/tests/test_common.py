from unittest import TestCase

import colander
import deform
from pyramid import testing

from madetomeasure.models.app import bootstrap_root


class AddTranslationsNodeTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()
        settings = self.config.registry.settings
        settings['available_languages'] = 'en sv fi'
        settings['default_timezone'] = 'UTC'
        self.config.include('madetomeasure.models.translations')

    def tearDown(self):
        testing.tearDown()

    @property
    def _fut(self):
        from madetomeasure.schemas.common import add_translations_node
        return add_translations_node

    def test_with_default(self):
        schema = _DummySchema()
        self._fut(schema, 'trans')
        self.assertIsInstance(schema['trans']['sv'].typ, colander.String)
        self.assertIsInstance(schema['trans']['sv'].widget, deform.widget.TextInputWidget)

    def test_specified_without_default(self):
        schema = _DummySchema()
        self._fut(schema, 'trans', based_on = 'first')
        self.assertEqual(schema['trans']['sv'].widget, None)
        self.assertEqual(schema['trans']['sv'].validator, None)
        self.assertIsInstance(schema['trans']['sv'].typ, colander.String)

    def test_specified_without_default(self):
        schema = _DummySchema()
        self._fut(schema, 'trans', based_on = 'second')
        self.assertIsInstance(schema['trans']['sv'].widget, deform.widget.CheckboxWidget)
        self.assertEqual(schema['trans']['sv'].validator, dummy_validator)
        self.assertIsInstance(schema['trans']['sv'].typ, colander.Bool)


@colander.deferred
def dummy_validator(node, kw):
    pass

class _DummySchema(colander.Schema):
    first = colander.SchemaNode(colander.String())
    second = colander.SchemaNode(colander.Bool(),
                                 widget = deform.widget.CheckboxWidget(),
                                 missing = False,
                                 title = "Checkbox",
                                 validator = dummy_validator,)
