import urllib
from uuid import uuid4

import deform
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.decorator import reify
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
from pyramid.url import resource_url
from pyramid.renderers import get_renderer
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound

from madetomeasure.interfaces import *
from madetomeasure.schemas import LoginSchema, CONTENT_SCHEMAS
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.models import CONTENT_TYPES


BASE_VIEW_TEMPLATE = 'templates/view.pt'
BASE_FORM_TEMPLATE = 'templates/form.pt'

#button_cancel = deform.Button('cancel', _(u"Cancel"))
#button_delete = deform.Button('delete', _(u"Delete"))
button_login = deform.Button('login', _(u"Login"))
button_save = deform.Button('save', _(u"Save"))


class View(object):

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

    @view_config(name='add', renderer=BASE_FORM_TEMPLATE)
    def add_view(self):
        #FIXME: Check permissions
        type_to_add = self.request.GET.get('content_type')
        if type_to_add not in self.addable_types():
            raise ValueError("No content type called %s" % type_to_add)

        schema = CONTENT_SCHEMAS["Add%s" % type_to_add]()
        schema = schema.bind()
        form = deform.Form(schema, buttons=(button_save,))
        
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

        self.response['form_resources'] = form.get_widget_resources()
        self.response['form'] = form.render()
        return self.response


    @view_config(name='edit', renderer=BASE_FORM_TEMPLATE)
    def edit_view(self):
        #FIXME: Check permissions

        schema = CONTENT_SCHEMAS["Edit%s" % self.context.content_type]()
        schema = schema.bind(context = self.context,)
        form = deform.Form(schema, buttons=(button_save,))
        
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

        self.response['form_resources'] = form.get_widget_resources()
        self.response['form'] = form.render(appstruct)
        return self.response


    @view_config(context=ISiteRoot, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=IUsers, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=ISurveys, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=IParticipants, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=IQuestions, renderer=BASE_VIEW_TEMPLATE)
    def admin_listing_view(self):
        return self.response

    @view_config(context=ISiteRoot, name='login', renderer=BASE_FORM_TEMPLATE)
    def login(self):
        
        login_schema = LoginSchema().bind(came_from = self.request.GET.get('came_from', ''),)
        
        form = deform.Form(login_schema, buttons=(button_login,))
        
        self.response['form_resources'] = form.get_widget_resources()
    
        POST = self.request.POST
        #Handle submitted information
        if 'login' in POST:
            controls = POST.items()
    
            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            userid = appstruct['userid']
            password = appstruct['password']
            came_from = urllib.unquote(appstruct['came_from'])
    
            user = self.root['users'].get(userid)
            
            if IUser.providedBy(user):
                if user.check_password(password):
                    headers = remember(self.request, user.__name__)
                    if came_from:
                        url = came_from
                    else:
                        url = resource_url(self.context, self.request)
                        
                    return HTTPFound(location = url,
                                     headers = headers)

        #Render login form            
        self.response['form'] = form.render()
        return self.response

    @view_config(context=ISiteRoot, name='logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location = resource_url(self.context, self.request),
                         headers = headers)