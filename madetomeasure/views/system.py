import urllib
from copy import deepcopy

import deform
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.url import resource_url
from pyramid.exceptions import Forbidden

from madetomeasure.interfaces import ISiteRoot
from madetomeasure.interfaces import ISurvey
from madetomeasure.interfaces import IUser
from madetomeasure.interfaces import IOrganisation
from madetomeasure.schemas.system import LoginSchema
from madetomeasure.schemas.system import RenameSchema
from madetomeasure.schemas.system import RequestPasswordSchema
from madetomeasure.schemas.system import TokenPasswordChange
from madetomeasure.schemas.system import PermissionSchema
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure import security
from madetomeasure.security import MANAGE_SERVER


class SystemView(BaseView):

    @view_config(context=ISiteRoot, name='login', renderer=BASE_FORM_TEMPLATE)
    def login(self):
        forgot_pw_msg = _(u"Forgot your password? ${pw_link}Click here to recover it.${pw_link_end}",
                          mapping = {'pw_link': '<a href="%s">' % self.request.resource_url(self.context, 'request_password'),
                                     'pw_link_end': '</a>'})
        login_schema = LoginSchema().bind(came_from = self.request.GET.get('came_from', ''), context = self.context, request = self.context)
        form = deform.Form(login_schema, buttons=(self.buttons['login'],))
        self.response['form_resources'] = form.get_widget_resources()

        POST = self.request.POST
        if 'login' in POST:
            controls = POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                self.add_flash_message(forgot_pw_msg)
                return self.response

            #userid here can be either an email address or a login name
            userid_or_email = appstruct['userid_or_email']
            if '@' in userid_or_email:
                #assume email
                user = self.context['users'].get_user_by_email(userid_or_email)
            else:
                user = self.context['users'].get(userid_or_email)
            password = appstruct['password']
            came_from = urllib.unquote(appstruct['came_from'])
            #Validation of user object provided by schema
            #FIXME: Do form validation for password instead
            if user.check_password(password):
                headers = remember(self.request, user.__name__)
                self.add_flash_message(_(u"Welcome"))
                if came_from:
                    url = came_from
                else:
                    url = resource_url(self.context, self.request)
                return HTTPFound(location = url,
                                 headers = headers)
            else:
                self.add_flash_message(_(u"Login incorrect"))
        #Render login form
        self.add_flash_message(forgot_pw_msg)    
        self.response['form'] = form.render()
        return self.response

    @view_config(context=ISiteRoot, name='logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location = resource_url(self.context, self.request),
                         headers = headers)
                         
    @view_config(context=ISiteRoot, name='request_password', renderer=BASE_FORM_TEMPLATE)
    def request_password(self):
        """ Request password form """
        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        schema = RequestPasswordSchema().bind(context = self.context, request = self.request)
        form = deform.Form(schema, buttons=(self.buttons['request'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()

        if 'request' in self.request.POST:
            controls = self.request.POST.items()
            try:
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
            #Validation is handled by validator in schema
            user.new_request_password_token(self.request)
            self.add_flash_message(_(u"Password change link emailed."))
            url = self.request.resource_url(self.context, 'login')
            return HTTPFound(location = url)
        self.response['form'] = form.render()
        return self.response
        
    @view_config(context=IUser, name="token_pw", renderer=BASE_FORM_TEMPLATE)
    def token_password_change(self):
        """ Token password change view """
        if 'cancel' in self.request.POST:
            url = resource_url(self.root, self.request)
            return HTTPFound(location=url)

        if self.context.__token__ == None:
            self.add_flash_message(_(u"You haven't requested a new password"))
            raise HTTPForbidden("Access to password token view not allowed if user didn't request password change.")

        schema = TokenPasswordChange(self.context)
        form = deform.Form(schema, buttons=(self.buttons['change'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()

        if 'change' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            self.context.remove_password_token()
            self.context.set_field_value('password', appstruct['password'])
            self.add_flash_message(_(u"Password changed, please login."))
            url = self.request.resource_url(self.root, 'login')
            return HTTPFound(location=url)

        #Fetch token from get request
        token = self.request.GET.get('token', None)
        if token is None:
            self.add_flash_message(_(u"Invalid security token. Did you click the link in your email?"))
            url = resource_url(self.root, self.request)
            return HTTPFound(location=url)

        #Everything seems okay. Render form
        appstruct = dict(token = token)
        self.response['form'] = form.render(appstruct=appstruct)
        return self.response

    @view_config(context=ISiteRoot, name="permissions", renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    @view_config(context=IOrganisation, name="permissions", renderer=BASE_FORM_TEMPLATE, permission=security.MANAGE_ORGANISATION)
    def permissions_form(self):
        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location=url)

        schema = PermissionSchema(self.context)
        form = deform.Form(schema, buttons=(self.buttons['save'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()

        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
                #FIXME: validate name - it must be unique and url-id-like
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response

            #Set permissions
            self.context.update_userids_permissions(appstruct['userids_and_groups'])
            self.add_flash_message(_(u"Saved"))

        #No action - Render edit form
        appstruct = dict(userids_and_groups=self.context.get_security())
        
        self.response['form'] = form.render(appstruct=appstruct)
        return self.response

    @view_config(context=ISurvey, name="rename", renderer=BASE_FORM_TEMPLATE, permission=MANAGE_SERVER)
    def rename_form(self):
        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location=url)

        if self.root == self.context:
            raise Forbidden("Can't change name of root")

        schema = RenameSchema().bind(context = self.context, request = self.request)
        form = deform.Form(schema, buttons=(self.buttons['save'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()

        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
                #FIXME: validate name - it must be unique and url-id-like
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            parent = self.context.__parent__
            parent[appstruct['name']] = deepcopy(self.context)
            del parent[self.context.__name__]
            
            new_context = parent[appstruct['name']]
            url = resource_url(new_context, self.request)
            return HTTPFound(location=url)

        #No action - Render edit form
        self.response['form'] = form.render(appstruct = {'name': self.context.__name__})
        return self.response
