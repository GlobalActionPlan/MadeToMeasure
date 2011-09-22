import urllib

import deform
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url
from pyramid.traversal import find_root 

from madetomeasure.interfaces import *
from madetomeasure.schemas.system import LoginSchema
from madetomeasure.schemas.system import RequestPasswordSchema
from madetomeasure.schemas.system import TokenPasswordChange
from madetomeasure.schemas.system import PermissionSchema
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure import security


class SystemView(BaseView):

    @view_config(context=ISiteRoot, name='login', renderer=BASE_FORM_TEMPLATE)
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
                         
    @view_config(context=ISiteRoot, name='request_password', renderer=BASE_FORM_TEMPLATE)
    def request_password(self):
        
        schema = RequestPasswordSchema().bind()
        form = deform.Form(schema, buttons=(self.buttons['request'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()
    
        #Handle submitted information
        if 'request' in self.request.POST:
            controls = self.request.POST.items()
    
            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            userid_or_email = appstruct['userid_or_email']
    
            #userid here can be either an email address or a login name
            if '@' in userid_or_email:
                #assume email
                user = self.context['users'].get_user_by_email(userid_or_email)
            else:
                user = self.context['users'].get(userid_or_email)
            
            if IUser.providedBy(user):
                user.new_request_password_token(self.request)
                url = resource_url(self.context, self.request)
                return HTTPFound(location = url)

        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)
    
        #Render form
        self.response['form'] = form.render()
        return self.response
        
    @view_config(context=IUser, name="token_pw", renderer=BASE_FORM_TEMPLATE)
    def token_password_change(self):
        
        schema = TokenPasswordChange(self.context)
        self.form = deform.Form(schema, buttons=(self.buttons['change'], self.buttons['cancel']))
        self.response['form_resources'] = self.form.get_widget_resources()

        post = self.request.POST
        if 'change' in post:
            controls = post.items()
            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = self.form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            self.context.remove_password_token()
            self.context.set_password(appstruct['password'])
            url = "%slogin" % resource_url(self.root, self.request)
            return HTTPFound(location=url)

        if 'cancel' in post:
            url = resource_url(self.root, self.request)
            return HTTPFound(location=url)

        #Fetch token from get request
        token = self.request.GET.get('token', None)
        if token is None:
            self.add_flash_message(_(u"Invalid security token. Did you click the link in your email?"))
            url = resource_url(self.root, self.request)
            return HTTPFound(location=url)

        #Everything seems okay. Render form
        appstruct = dict(token = token)
        self.response['form'] = self.form.render(appstruct=appstruct)
        return self.response
        
    def get_permission_appstruct(self, context):
        """ Return the current settings in a structure that is usable in a deform form.
        """
        root = find_root(context)
        users = root['users']
        appstruct = {}

        userids_and_groups = []
        for userid in context._groups:
            user = users[userid]
            userids_and_groups.append({'userid':userid, 'groups':context.get_groups(userid)})
        appstruct['userids_and_groups'] = userids_and_groups

        return appstruct
        
    @view_config(context=ISiteRoot, name="permissions", renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    @view_config(context=IOrganisation, name="permissions", renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def permissions_form(self):

        schema = PermissionSchema(self.context)
        self.form = deform.Form(schema, buttons=(self.buttons['save'], self.buttons['cancel']))
        self.response['form_resources'] = self.form.get_widget_resources()

        post = self.request.POST
        if 'save' in post:
            controls = post.items()
            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = self.form.validate(controls)
                #FIXME: validate name - it must be unique and url-id-like
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            #Set permissions
            self.context.update_userids_permissions(appstruct['userids_and_groups'])
            
        if 'cancel' in post:
            url = resource_url(self.context, self.request)
            return HTTPFound(location=url)

        #No action - Render edit form
        appstruct = self.get_permission_appstruct(self.context)
        
        self.response['form'] = self.form.render(appstruct=appstruct)
        return self.response
