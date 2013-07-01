from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform.exception import ValidationFailure
from betahaus.pyracont.factories import createContent
from betahaus.pyracont.factories import createSchema

from madetomeasure.interfaces import IChoice
from madetomeasure.interfaces import IChoiceQuestionType
from madetomeasure.interfaces import IQuestionType
from madetomeasure.interfaces import IQuestionTypes
from madetomeasure import security
from madetomeasure.views.base import BaseView
from madetomeasure.schemas.common import add_translations_node

BASE_VIEW_TEMPLATE = 'templates/view.pt'
BASE_FORM_TEMPLATE = 'templates/form.pt'


class QuestionTypesView(BaseView):

    @view_config(name='add', context=IQuestionTypes, renderer=BASE_FORM_TEMPLATE, permission = security.EDIT)
    def add_type_view(self):
        """ Add view for question types. Works like a wizard.
        """
        type_to_add = self.request.GET.get('content_type')

        if 'cancel' in self.request.POST:
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)

        schema = createSchema('AddQuestionTypeSchema')
        schema = schema.bind(context=self.context, request=self.request)

        form = Form(schema, buttons=(self.buttons['save'], self.buttons['cancel'], ))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            appstruct['creators'] = [self.userid]
            obj = createContent(type_to_add, **appstruct)
            self.context[obj.uid] = obj
            url = self.request.resource_url(obj, 'edit')
            return HTTPFound(location = url)
        self.response['form'] = form.render()
        return self.response

    @view_config(context=IQuestionType, renderer='templates/question_type.pt', permission=security.VIEW)
    def question_type_view(self):
        self.response['choices'] = [x for x in self.context.values() if IChoice.providedBy(x)]
        return self.response

    @view_config(name='add', context=IChoiceQuestionType, renderer=BASE_FORM_TEMPLATE, permission = security.EDIT)
    def add_choice(self):
        """ Add a choice
        """
        #FIXME: Refactor and make generic. Translation node needs to go to edit as well
        type_to_add = self.request.GET.get('content_type')

        if 'cancel' in self.request.POST:
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)

        schema = createSchema('ChoiceSchema')
        add_translations_node(schema, 'title_translations')
        schema = schema.bind(context = self.context, request = self.request)

        form = Form(schema, buttons = (self.buttons['save'], self.buttons['cancel'], ))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            appstruct['creators'] = [self.userid]
            if appstruct.get('ignore_translations', None):
                del appstruct['title_translations']
            obj = createContent(type_to_add, **appstruct)
            self.context[obj.uid] = obj
            url = self.request.resource_url(obj)
            return HTTPFound(location = url)
        self.response['form'] = form.render()
        return self.response
