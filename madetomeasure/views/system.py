import urllib

import deform
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url

from madetomeasure.interfaces import *
from madetomeasure.schemas.system import LoginSchema
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView


class SystemView(BaseView):

    @view_config(context=ISiteRoot, name='login', renderer='templates/form.pt')
    def login(self):
        
        login_schema = LoginSchema().bind(came_from = self.request.GET.get('came_from', ''),)
        
        form = deform.Form(login_schema, buttons=(self.buttons['login'],))
        
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
