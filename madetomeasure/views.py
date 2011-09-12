import urllib

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
from madetomeasure.schemas import LoginSchema
from madetomeasure import MadeToMeasureTSF as _

BASE_VIEW_TEMPLATE = 'templates/view.pt'
BASE_FORM_TEMPLATE = 'templates/form.pt'

#button_cancel = deform.Button('cancel', _(u"Cancel"))
#button_delete = deform.Button('delete', _(u"Delete"))
button_login = deform.Button('login', _(u"Login"))


class View(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.response = dict(
            userid = self.userid,
            main_macro = self.main_macro,
            resource_url = resource_url,
            root = self.root,
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


    @view_config(context=ISiteRoot, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=IUsers, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=ISurveys, renderer=BASE_VIEW_TEMPLATE)
    @view_config(context=IParticipants, renderer=BASE_VIEW_TEMPLATE)
    def admin_listing_view(self):
        return self.response

    @view_config(context=ISiteRoot, name='login', renderer=BASE_FORM_TEMPLATE)
    def login(self):
        
        login_schema = LoginSchema()
        login_schema.bind(came_from = self.request.GET.get('came_from', ''),)
        
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