from uuid import uuid4

from colander import Schema
from deform import Form
from deform.exception import ValidationFailure
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url
from pyramid.security import has_permission

from madetomeasure.interfaces import *
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_VIEW_TEMPLATE
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure.models import CONTENT_TYPES
from madetomeasure.schemas import CONTENT_SCHEMAS
from madetomeasure import security


class QuestionsView(BaseView):

    @view_config(name='add', context=IQuestions, renderer=BASE_FORM_TEMPLATE)
    def add_view(self):
        type_to_add = self.request.GET.get('content_type')
        
        #Permission check
        add_permission = "Add %s" % type_to_add
        if not has_permission(add_permission, self.context, self.request):
            raise Forbidden("You're not allowed to add '%s' in this context." % type_to_add)
            
        if type_to_add not in self.addable_types():
            raise ValueError("No content type called %s" % type_to_add)

        schema = CONTENT_SCHEMAS["Add%s" % type_to_add]()
        schema = schema.bind()
        
        self.trans_util.add_translations_schema(schema['question_text'])

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
            
            obj = CONTENT_TYPES[type_to_add]()
            for (k, v) in appstruct.items():
                mutator = getattr(obj, 'set_%s' % k)
                mutator(v)
            
            self.context[str(uuid4())] = obj
    
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        self.response['form'] = form.render()
        return self.response


    @view_config(name='edit', context=IQuestion, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def edit_view(self):

        schema = CONTENT_SCHEMAS["Edit%s" % self.context.content_type]()
        schema = schema.bind(context = self.context,)
        self.trans_util.add_translations_schema(schema['question_text'])
        
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
            
            for (k, v) in appstruct.items():
                mutator = getattr(self.context, 'set_%s' % k)
                mutator(v)
                
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        marker = object()
        appstruct = {}
        for field in schema:
            accessor = getattr(self.context, "get_%s" % field.name, marker)
            if accessor != marker:
                appstruct[field.name] = accessor()

        self.response['form'] = form.render(appstruct)
        return self.response
        
    @view_config(context=IQuestions, renderer='templates/questions.pt', permission=security.VIEW)
    def admin_listing_view(self):
        
        types = {}
        for (name, util) in self.request.registy.getUtilitiesFor(IQuestionNode):
            types[name] = {}
            types[name]['name'] = getattr(util, 'type_title', '')
            #FIXME: Use for local questions too
            types[name]['questions'] = self.context.questions_by_type(name)
            
        self.response['types'] = types
        
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
        schema = schema.bind(context = self.context,)
        self.trans_util.add_translation_schema(schema['question_text'], lang)
        
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
            
            for (lang, value) in appstruct['question_text'].items():
                self.context.set_question_text_lang(value, lang)
            
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        marker = object()
        appstruct = {}
        for field in schema:
            accessor = getattr(self.context, "get_%s" % field.name, marker)
            if accessor != marker:
                appstruct[field.name] = accessor()

        self.response['form'] = form.render(appstruct)
        return self.response
