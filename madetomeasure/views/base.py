from pyramid.decorator import reify
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
from pyramid.url import resource_url
from pyramid.renderers import get_renderer
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from deform import Button
from deform import Form
from colander import Schema

from madetomeasure.models.app import generate_slug
from madetomeasure.interfaces import *
from madetomeasure.schemas import LoginSchema, CONTENT_SCHEMAS
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.models import CONTENT_TYPES


BASE_VIEW_TEMPLATE = 'templates/view.pt'
BASE_FORM_TEMPLATE = 'templates/form.pt'

class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = dict(
            userid = self.userid,
            main_macro = self.main_macro,
            resource_url = resource_url,
            root = self.root,
            addable_types = self.addable_types(),
        )

    @reify
    def userid(self):
        return authenticated_userid(self.request)

    @reify
    def root(self):
        return find_root(self.context)
    
    @reify
    def main_macro(self):
        return get_renderer('templates/main.pt').implementation().macros['master']
    
    def addable_types(self):
        #FIXME: Check permission?
        context_type = getattr(self.context, 'content_type', '')
        addable = []
        for (type, klass) in CONTENT_TYPES.items():
            if context_type in klass.allowed_contexts:
                addable.append(type)
        return addable

    @reify
    def buttons(self):
        buttons = {}
        buttons['login'] = Button('login', _(u"Login"))
        buttons['save'] = Button('save', _(u"Save"))
        buttons['send'] = Button('send', _(u"Send"))
        buttons['next'] = Button('next', _(u"Next"))
        buttons['previous'] = Button('previous', _(u"Previous"))
        buttons['cancel'] = Button('cancel', _(u"Cancel"))
        buttons['request'] = Button('request', _(u"Request"))
        buttons['change'] = Button('change', _(u"Change"))
        
        return buttons

    @view_config(context=ISiteRoot, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=IUsers, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=ISurveys, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=ISurveySection, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=ISurvey, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=IParticipants, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=IOrganisation, renderer=BASE_VIEW_TEMPLATE)
    def admin_listing_view(self):
        #FIXME: move when implemented
        return self.response

    @view_config(context=IUser, renderer=BASE_VIEW_TEMPLATE)
    def admin_view(self):
        #FIXME: Should probably not exist at all :)
        return self.response


    @view_config(name="delete", renderer="templates/form.pt")
    def delete_form(self):
        #FIXME: This is temporary!
        
        schema = Schema()
        
        form = Form(schema, buttons=('delete',))
        self.response['form_resources'] = form.get_widget_resources()

        post = self.request.POST
        if 'delete' in post:
            parent = self.context.__parent__
            del parent[self.context.__name__]

            url = resource_url(parent, self.request)
            return HTTPFound(location=url)

        self.response['form'] = form.render()
        return self.response


    @view_config(name='add', context=ISurveys, renderer=BASE_FORM_TEMPLATE)
    @view_config(name='add', context=ISurvey, renderer=BASE_FORM_TEMPLATE)
    @view_config(name='add', context=ISiteRoot, renderer=BASE_FORM_TEMPLATE)
    def add_view(self):
        """ Generic add view when accessors and mutators match get_ and set_ methods
            on the model.
        """
        #FIXME: Check permissions

        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)
        
        type_to_add = self.request.GET.get('content_type')
        if type_to_add not in self.addable_types():
            raise ValueError("No content type called %s" % type_to_add)

        schema = CONTENT_SCHEMAS["Add%s" % type_to_add]()
        schema = schema.bind()
        form = Form(schema, buttons=(self.buttons['save'], self.buttons['cancel'], ))
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
            
            name = generate_slug(self.context, obj.get_title())
            self.context[name] = obj
    
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        self.response['form'] = form.render()
        return self.response


    @view_config(name='edit', context=ISurvey, renderer=BASE_FORM_TEMPLATE)
    @view_config(name='edit', context=ISurveySection, renderer=BASE_FORM_TEMPLATE)
    @view_config(name='edit', context=IOrganisation, renderer=BASE_FORM_TEMPLATE)
    def edit_view(self):
        """ Generic edit view when accessors and mutators match get_ and set_ methods
            on the model.
        """
        #FIXME: Check permissions

        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        def _question_types():
            #FIXME: Handle several?
            if hasattr(self.context, 'get_question_type'):
                return [self.context.get_question_type()]

        schema = CONTENT_SCHEMAS["Edit%s" % self.context.content_type]()
        schema = schema.bind(context = self.context,
                             question_types = _question_types())
                
        form = Form(schema, buttons=(self.buttons['save'], self.buttons['cancel'], ))
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
    