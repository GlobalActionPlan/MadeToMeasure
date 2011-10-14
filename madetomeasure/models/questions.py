from zope.interface import implements
from BTrees.OOBTree import OOBTree
from zope.component import getUtility
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_interface

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *
from madetomeasure.models.base import BaseFolder



class Questions(BaseFolder):
    implements(IQuestions)
    content_type = 'Questions'
    display_name = _(u"Questions")
    allowed_contexts = ()
    
    def get_title(self):
        return self.display_name

    def set_title(self, value):
        pass

    def questions_by_type(self, question_type):
        """ Return available question objects according to a specific type. """
        results = set()
        for obj in self.values():
            if not IQuestion.providedBy(obj):
                continue
            if obj.get_question_type() == question_type:
                results.add(obj)
        return results

class Question(BaseFolder):
    implements(IQuestion)
    content_type = 'Question'
    display_name = _(u"Question")
    allowed_contexts = ('Questions', )

    def __init__(self):
        self.__question_text__ = OOBTree()
        super(Question, self).__init__()
        
    def get_title(self, lang=None, context=None):
        # if context is supplied find organisation and look if there is 
        # a variant for the question for lang
        if context:
            if lang:
                local_lang = lang
            else:
                request = get_current_request()
                trans_util = request.registry.getUtility(IQuestionTranslations)
                local_lang = trans_util.default_locale_name
            organisation = find_interface(context, IOrganisation)
            if organisation:
                variant = organisation.get_variant(self.__name__, local_lang)
                if variant:
                    return variant
        if lang:
            languages = self.get_question_text()
            if lang in languages:
                return languages[lang]
        return getattr(self, '__title__', '')
    
    def get_question_text(self):
        return getattr(self, '__question_text__', {})

    def set_question_text(self, value):
        """ This is only for the translations of the question, since the title is the base language.
            value here should be a dict with country codes as keys and questions as values.
            Any empty value should be removed before saving.
        """
        for (k, v) in value.items():
            if not v.strip():
                del value[k]
        self.__question_text__ = value
        
    def set_question_text_lang(self, value, lang):
        """ Set translation for specific language
        """
        question_text = self.get_question_text()
        if value:
            question_text[lang] = value
        else:
            if lang in question_text:
                del question_text[lang]
        self.__question_text__ = question_text
    
    def get_question_type(self):
        """ Return a dict with country codes as key and question translations as value. """
        return getattr(self, '__question_type__', '')
    
    def set_question_type(self, value):
        self.__question_type__ = value

    def question_schema_node(self, name, lang=None, context=None):
        #If the correct question type isn't set, this might raise a ComponentLookupError
        node_util = getUtility(IQuestionNode, name=self.get_question_type())
        return node_util.node(name, title=self.get_title(lang, context=context))

    def render_result(self, request, data):
        if not data:
            return _(u"(Nothing)")
        node_util = getUtility(IQuestionNode, name=self.get_question_type())
        return node_util.render_result(request, data)
        
    def csv_export(self, data):
        node_util = getUtility(IQuestionNode, name=self.get_question_type())
        return node_util.csv_export(data)
        
