from pyramid.view import view_config

from madetomeasure.interfaces import IChoice
from madetomeasure.interfaces import IQuestionType
from madetomeasure import security
from madetomeasure.views.base import BaseView


class QuestionTypesView(BaseView):

    @view_config(context=IQuestionType, renderer='templates/question_type.pt', permission=security.VIEW)
    def question_type_view(self):
        self.response['choices'] = [x for x in self.context.values() if IChoice.providedBy(x)]
        return self.response
