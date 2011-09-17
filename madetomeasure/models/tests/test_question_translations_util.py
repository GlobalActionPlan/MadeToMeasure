import unittest

import colander
from pyramid import testing
from zope.interface.verify import verifyObject


class QuestionTranslationsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.translations import QuestionTranslations
        settings = dict(default_locale_name='en',
                        available_languages='en sv de ru',)
        return QuestionTranslations(settings)

    def test_interface(self):
        from madetomeasure.interfaces import IQuestionTranslations
        obj = self._make_obj()
        self.assertTrue(verifyObject(IQuestionTranslations, obj))

    def test_title_for_code(self):
        obj = self._make_obj()
        self.assertEqual(obj.title_for_code('sv'), u"svenska")
        self.assertEqual(obj.title_for_code('en'), u"English")
        #This is a translation string so it will look like this untranslated
        self.assertEqual(obj.title_for_code('404_lang'), u"Country code: ${country_code}")

    def test_add_translations_schema(self):
        obj = self._make_obj()
        schema = colander.Schema()
        
        obj.add_translations_schema(schema)
        
        childrens_names = set([x.name for x in schema.children])
        self.assertEqual(childrens_names, set(['sv', 'de', 'ru']))
        
        self.assertEqual(schema['ru'].title, u"\u0440\u0443\u0441\u0441\u043a\u0438\u0439")
        self.assertEqual(schema['sv'].title, u"svenska")

    def test_registration(self):
        #The util needs a few things in settings to work
        from pyramid.interfaces import ISettings
        settings = self.config.registry.getUtility(ISettings)
        settings['default_locale_name'] = 'en'
        settings['available_languages'] = 'sv de'
        
        from madetomeasure.interfaces import IQuestionTranslations
        self.config.include('madetomeasure.models.translations')
        
        self.assertTrue(self.config.registry.queryUtility(IQuestionTranslations))
