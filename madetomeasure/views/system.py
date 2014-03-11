from copy import deepcopy

from pyramid.view import view_config
from pyramid.decorator import reify
from pyramid.security import remember
from pyramid.security import forget
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from betahaus.pyracont.factories import createSchema

from madetomeasure.interfaces import ISiteRoot
from madetomeasure.interfaces import ISurvey
from madetomeasure.interfaces import IUser
from madetomeasure.interfaces import IOrganisation
from madetomeasure.schemas.validators import deferred_login_validator
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseForm
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure import security
from madetomeasure.security import MANAGE_SERVER


@view_config(context=ISiteRoot, name='login', renderer=BASE_FORM_TEMPLATE)
class LoginForm(BaseForm):

    @reify
    def schema(self):
        schema = createSchema('LoginSchema')
        schema.validator = deferred_login_validator
        return schema

    @reify
    def buttons(self):
        return (self.button_login, self.button_forgot_pw, self.button_cancel,)

    def login_success(self, appstruct):
        userid_or_email = appstruct['userid_or_email']
        if '@' in userid_or_email:
            #assume email
            user = self.context['users'].get_user_by_email(userid_or_email)
        else:
            user = self.context['users'].get(userid_or_email)
        assert user is not None
        headers = remember(self.request, user.__name__)
        self.add_flash_message(_(u"Welcome"))
        came_from = self.request.GET.get('came_from', '')
        if came_from:
            url = came_from
        else:
            url = self.request.resource_url(self.context)
        return HTTPFound(location = url, headers = headers)

    def forgot_pw_success(self, appstruct):
        return HTTPFound(location = self.request.resource_url(self.context, 'request_password'))
    forgot_pw_failure = forgot_pw_success


@view_config(context=ISiteRoot, name='request_password', renderer=BASE_FORM_TEMPLATE)
class RequestPasswordForm(BaseForm):

    @reify
    def schema(self):
        return createSchema('RequestPasswordSchema')

    @reify
    def buttons(self):
        return (self.button_request, self.button_cancel,)

    def request_success(self, appstruct):
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


@view_config(context=IUser, name="token_pw", renderer=BASE_FORM_TEMPLATE)
class TokenPasswordChangeForm(BaseForm):

    def __call__(self):
        try:
            #FIXME: This will probably change
            self.context.validate_password_token(None, self.request.GET.get('token', ''))
        except ValueError:
            self.add_flash_message(_(u"You haven't requested a new password"))
            raise HTTPForbidden("Access to password token view not allowed if user didn't request password change.")
        return super(TokenPasswordChangeForm, self).__call__()

    @reify
    def schema(self):
        return createSchema('TokenPasswordChange')

    @reify
    def buttons(self):
        return (self.button_change, self.button_cancel,)

    def change_success(self, appstruct):
        self.context.remove_password_token()
        self.context.set_field_value('password', appstruct['password'])
        self.add_flash_message(_(u"Password changed, please login."))
        url = self.request.resource_url(self.root, 'login')
        return HTTPFound(location = url)


@view_config(context=ISiteRoot, name="permissions", renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
@view_config(context=IOrganisation, name="permissions", renderer=BASE_FORM_TEMPLATE, permission=security.MANAGE_ORGANISATION)
class PermissionsForm(BaseForm):

    @reify
    def schema(self):
        return createSchema('PermissionsSchema')

    @reify
    def buttons(self):
        return (self.button_save, self.button_cancel,)

    def appstruct(self):
        return dict(userids_and_groups = self.context.get_security())

    def save_success(self, appstruct):
        self.context.update_userids_permissions(appstruct['userids_and_groups'])
        self.add_flash_message(self.default_success)
        url = self.request.resource_url(self.context)
        return HTTPFound(location = url)


@view_config(context=ISurvey, name="rename", renderer=BASE_FORM_TEMPLATE, permission=MANAGE_SERVER)
class RenameForm(BaseForm):

    def __call__(self):
        if self.root == self.context:
            raise HTTPForbidden("Can't change name of root")
        return super(RenameForm, self).__call__()

    @reify
    def schema(self):
        return createSchema('RenameSchema')

    @reify
    def buttons(self):
        return (self.button_save, self.button_cancel,)

    def appstruct(self):
        return {'name': self.context.__name__}

    def save_success(self, appstruct):
        parent = self.context.__parent__
        parent[appstruct['name']] = deepcopy(self.context)
        del parent[self.context.__name__]
        new_context = parent[appstruct['name']]
        self.add_flash_message(self.default_success)
        url = self.request.resource_url(new_context)
        return HTTPFound(location=url)


class SystemView(BaseView):

    @view_config(context=ISiteRoot, name='logout')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location = self.request.resource_url(self.context),
                         headers = headers)
