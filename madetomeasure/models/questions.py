from zope.interface import implements
from BTrees.OOBTree import OOBTree
from zope.component import getUtility

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *
from madetomeasure.models.base import BaseFolder



class Questions(BaseFolder):
    implements(IQuestions)
    content_type = 'Questions'
    display_name = _(u"Questions")
    allowed_contexts = () #Not manually addable
    
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
    
    def get_question_text(self):
        results = []
        for (lang, text) in self.__question_text__.items():
            results.append({'lang':lang,'text':text})
        return results

    def set_question_text(self, value):
        """ Example value: [{'lang': u'sv', 'text': u'Svensk text'}]
            This is only for the translations of the question, since the title is the base language.
        """
        new_keys = [x['lang'] for x in value]
        for entry in value:
            self.__question_text__[entry['lang']] = entry['text']
        #Remove any keys not present in the form. They've been deleted
        for k in self.__question_text__.keys():
            if k not in new_keys:
                del self.__question_text__[k]
    
    def get_question_type(self):
        return getattr(self, '__question_type__', '')
    
    def set_question_type(self, value):
        self.__question_type__ = value

    def question_schema_node(self, name, lang=None):
        #If the correct question type isn't set, this might raise a ComponentLookupError
        node_util = getUtility(IQuestionNodeFactory, name=self.get_question_type())
        #FIXME: Update with lang
        return node_util.node(name, title=self.get_title())

    def render_result(self, request, data):
        if not data:
            return _(u"(Nothing)")
        node_util = getUtility(IQuestionNode, name=self.get_question_type())
        return node_util.render_result(request, data)
        