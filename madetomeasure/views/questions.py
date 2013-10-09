from colander import Schema
from deform import Form
from pyramid.view import view_config
from betahaus.pyracont.factories import createSchema

from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IQuestion
from madetomeasure.interfaces import IQuestions
from madetomeasure.views.base import BaseView
from madetomeasure import security


class QuestionsView(BaseView):
        
    @view_config(context=IQuestions, renderer='templates/questions.pt', permission=security.VIEW)
    @view_config(name="variants", context=IOrganisation, renderer='templates/questions.pt', permission=security.VIEW)
    def questions_view(self):
        """ This view is for any IQuestions context, both the global one and the local one + the Organisation objects 'variants' view.
        """
        schema = createSchema('QuestionSearchSchema').bind(context = self.context, request = self.request)
        form = Form(schema, buttons = (), formid = 'tag_select', action = 'javascript:')
        self.response['form_resources'] = form.get_widget_resources()
        self.response['tag_form'] = form.render()
        #Get questions, sorted - behaves differently for variants!
        if IOrganisation.providedBy(self.context):
            questions = self.root['questions'].values()
        else:
            questions = self.context.values()
        self.response['questions'] = sorted(questions, key = lambda q: q.get_field_value('title').lower())
        self.response['is_org'] = IOrganisation.providedBy(self.context)
        self.response['show_edit_variants'] = self.response['is_org'] and \
            security.context_has_permission(self.context, security.MANAGE_SURVEY, self.userid)
        self.response['show_edit'] = IQuestions.providedBy(self.context) and \
            security.context_has_permission(self.context, security.EDIT, self.userid) or False
        return self.response
    
    @view_config(context=IQuestion, renderer='templates/survey_form.pt', permission=security.VIEW)
    def admin_view(self):
        schema = Schema()
        schema.add(self.context.question_schema_node('dummy'))
        form = Form(schema)
        self.response['form_resources'] = form.get_widget_resources()
        self.response['dummy_form'] = form.render()
        return self.response
