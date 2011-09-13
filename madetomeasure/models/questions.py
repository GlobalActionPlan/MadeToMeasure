from zope.interface import implements
from BTrees.OOBTree import OOBTree

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *
from madetomeasure.models.base import BaseFolder
from madetomeasure.schemas import QUESTION_SCHEMAS



class Questions(BaseFolder):
    implements(IQuestions)
    content_type = 'Questions'
    display_name = _(u"Questions")
    allowed_contexts = () #Not manually addable
    
    def get_title(self):
        return self.display_name

    def set_title(self, value):
        pass

class Question(BaseFolder):
    implements(IQuestion)
    content_type = 'Question'
    display_name = _(u"Question")
    allowed_contexts = ('Questions', )

    def __init__(self):
        self.__question_text__ = OOBTree()
        self.__question_type_schema__ = ''
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
    
    def get_question_type_schema(self):
        return self.__question_type_schema__
    
    def set_question_type_schema(self, value):
        self.__question_type_schema__ = value

    def get_schema(self, lang):
        """ Get a question schema with 'text' as the translated text of the question. """
        title = self.__question_text__.get(lang, None)
        if title is None:
            title = self.get_title()
        schema_type = self.get_question_type_schema()
        if schema_type not in QUESTION_SCHEMAS:
            raise KeyError("There's no schema called %s in QUESTION_SCHEMAS" % schema_type)
        return QUESTION_SCHEMAS[schema_type]().bind(question_title = title)
