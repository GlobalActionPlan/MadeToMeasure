from colander import Schema
from deform import Form
from deform.exception import ValidationFailure
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import has_permission

from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IQuestion
from madetomeasure.interfaces import IQuestions

from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure.models import CONTENT_TYPES
from madetomeasure.schemas import CONTENT_SCHEMAS
from madetomeasure.schemas.questions import QuestionSearchSchema
from madetomeasure import security


class QuestionsView(BaseView):

    @view_config(name='add', context=IQuestions, renderer=BASE_FORM_TEMPLATE)
    def add_view(self):
        type_to_add = self.request.GET.get('content_type')
        
        #Permission check
        add_permission = "Add %s" % type_to_add
        if not has_permission(add_permission, self.context, self.request):
            raise HTTPForbidden("You're not allowed to add '%s' in this context." % type_to_add)
            
        if type_to_add not in self.addable_types():
            raise ValueError("No content type called %s" % type_to_add)

        schema = CONTENT_SCHEMAS["Add%s" % type_to_add]()
        schema = schema.bind(context = self.context, request = self.request)
        
        self.trans_util.add_translations_schema(schema['question_text'], self.context)

        form = Form(schema, buttons=(self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()

            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            obj = CONTENT_TYPES[type_to_add](**appstruct)
            self.context[obj.uid] = obj
    
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)

        self.response['form'] = form.render()
        return self.response


    @view_config(name='edit', context=IQuestion, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def edit_view(self):

        schema = CONTENT_SCHEMAS["Edit%s" % self.context.content_type]()
        schema = schema.bind(context = self.context, request = self.request)
        self.trans_util.add_translations_schema(schema['question_text'], self.context)
        
        form = Form(schema, buttons=(self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()

            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response

            self.context.set_field_appstruct(appstruct)
                
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)

        appstruct = self.context.get_field_appstruct(schema)
        self.response['form'] = form.render(appstruct)
        return self.response
        
    @view_config(context=IQuestions, renderer='templates/questions.pt', permission=security.VIEW)
    @view_config(name="variants", context=IOrganisation, renderer='templates/questions.pt', permission=security.VIEW)
    def questions_view(self):
        schema = QuestionSearchSchema().bind(context = self.context, request = self.request)
        form = Form(schema, buttons = (), formid = 'tag_select', action = 'javascript:')
        self.response['form_resources'] = form.get_widget_resources()
        self.response['tag_form'] = form.render()
        
        #Get questions, sorted
        self.response['questions'] = sorted(self.root['questions'].values(), key = lambda q: q.get_field_value('title').lower())
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

        schema = CONTENT_SCHEMAS["Translate%s" % self.context.content_type]()
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
