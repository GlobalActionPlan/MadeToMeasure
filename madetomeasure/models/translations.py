from copy import copy

import colander
from pyramid.threadlocal import get_current_registry
from zope.interface import implements
from pyramid.interfaces import ISettings
from babel.localedata import load

from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure import MadeToMeasureTSF as _



class QuestionTranslations(object):
    """ Util to help out with managing runtime translations of questions. """
    implements(IQuestionTranslations)
    
    def __init__(self, settings=None):
        if settings is None:
            #To allow override and make it easier to run tests.
            reg = get_current_registry()
            settings = reg.getUtility(ISettings)

        self.default_locale_name = settings['default_locale_name'].strip()
        available_languages = [x for x in settings['available_languages'].split()]
        
        translatable_languages = copy(available_languages)
        if self.default_locale_name in translatable_languages:
            translatable_languages.remove(self.default_locale_name)
        
        self.available_languages = tuple(available_languages)
        self.translatable_languages = tuple(translatable_languages)
        
        self.lang_names = {}
        self.default_lang_names = {}
        for lang in self.available_languages:
            data = load(lang)
            self.lang_names[lang] = data['languages'][lang]
            data = load(self.default_locale_name)
            self.default_lang_names[lang] = data['languages'][lang]

    def title_for_code(self, lang):
        if lang in self.lang_names:
            return self.lang_names[lang]
        return _(u"Country code: ${country_code}", mapping={'country_code':lang})
        
    def title_for_code_default(self, lang):
        if lang in self.default_lang_names:
            return self.default_lang_names[lang]
        return _(u"Country code: ${country_code}", mapping={'country_code':lang})

    def add_translations_schema(self, schema):
        """ Fetch all possible translations (according to settings)
            and create a schema with each lang as a node.
        """
        for lang in self.translatable_languages:
            self.add_translation_schema(schema, lang)
                                           
    def add_translation_schema(self, schema, lang):
        """ Sreate a schema with lang as a node.
        """
        schema.add(colander.SchemaNode(colander.String(),
                                       name=lang,
                                       title=self.title_for_code(lang),
                                       missing=u"",))

def includeme(config):
    """ Register QuestionTranslations utility. """
    qt = QuestionTranslations(config.registry.settings)
    config.registry.registerUtility(qt, IQuestionTranslations)
