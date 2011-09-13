from zope.interface import implements

from madetomeasure.models.base import BaseFolder
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *



class Surveys(BaseFolder):
    implements(ISurveys)
    content_type = 'Surveys'
    display_name = _(u"Surveys")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name

    def set_title(self, value):
        pass


class Survey(BaseFolder):
    implements(ISurvey)
    content_type = 'Survey'
    display_name = _(u"Survey")
    allowed_contexts = ('Surveys',)


class SurveySection(BaseFolder):
    implements(ISurvey)
    content_type = 'SurveySection'
    display_name = _(u"Survey Section")
    allowed_contexts = ('Survey',)

    def get_question_type(self):
        return getattr(self, '__question_type__', '')
    
    def set_question_type(self, value):
        self.__question_type__ = value

    def get_question_ids(self):
        return getattr(self, '__question_ids__', set())

    def set_question_ids(self, value):
        self.__question_ids__ = value
    