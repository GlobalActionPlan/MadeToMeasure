from colander import Schema
from deform import Form
from deform.exception import ValidationFailure
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from betahaus.pyracont.factories import createSchema

from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IQuestion
from madetomeasure.interfaces import IQuestions

from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure.schemas.questions import QuestionSearchSchema
from madetomeasure import security


class QuestionsView(BaseView):
        
    @view_config(context=IQuestions, renderer='templates/questions.pt', permission=security.VIEW)
    @view_config(name="variants", context=IOrganisation, renderer='templates/questions.pt', permission=security.VIEW)
    def questions_view(self):
        """ This view is for any IQuestions context, both the global one and the local one + the Organisation objects 'variants' view.
        """
        schema = QuestionSearchSchema().bind(context = self.context, request = self.request)
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
        self.response['show_edit'] = security.context_has_permission(self.root['questions'], security.EDIT, self.userid)
        return self.response
    
    @view_config(context=IQuestion, renderer='templates/survey_form.pt', permission=security.VIEW)
    def admin_view(self):
        schema = Schema()
        schema.add(self.context.question_schema_node('dummy'))
        form = Form(schema)
        self.response['form_resources'] = form.get_widget_resources()
        self.response['dummy_form'] = form.render()
        return self.response
        
    @view_config(name='translate', context=IQuestion, renderer=BASE_FORM_TEMPLATE, permission=security.TRANSLATE)
    def translate_view(self):
        lang = self.request.GET['lang']
        schema = createSchema(self.context.schemas['translate'])
        schema = schema.bind(context = self.context, request = self.request)
        self.trans_util.add_translation_schema(schema['question_text'], lang)
        form = Form(schema, buttons=(self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()

        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            for (lang, value) in appstruct['question_text'].items():
                self.context.set_question_text_lang(value, lang)
            
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)

        appstruct = self.context.get_field_appstruct(schema)
        self.response['form'] = form.render(appstruct)
        return self.response
