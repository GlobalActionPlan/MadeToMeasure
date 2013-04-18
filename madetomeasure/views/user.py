from deform import Form
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url
from pyramid.security import has_permission
from pyramid.exceptions import Forbidden

from madetomeasure.interfaces import *
from madetomeasure import MadeToMeasureTSF as _

from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_VIEW_TEMPLATE
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure.models import CONTENT_TYPES
from madetomeasure.schemas import CONTENT_SCHEMAS
from madetomeasure.schemas.users import ChangePasswordSchema
from madetomeasure import security


class UsersView(BaseView):
    @view_config(context=IUser, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    def admin_view(self):
        schema = CONTENT_SCHEMAS["EditUser"]()
        schema = schema.bind(context = self.context, request = self.request)
        appstruct = self.context.get_field_appstruct(schema)                
        form = Form(schema, buttons=())
        self.response['form_resources'] = form.get_widget_resources()
        self.response['form'] = form.render(readonly = True, appstruct = appstruct)
        self.response['listing'] = self.listing_sniplet()
        return self.response

    @view_config(name='add', context=IUsers, renderer=BASE_FORM_TEMPLATE)
    def add_view(self):
        type_to_add = self.request.GET.get('content_type')

        #Permission check
        add_permission = "Add %s" % type_to_add
        if not has_permission(add_permission, self.context, self.request):
            raise Forbidden("You're not allowed to add '%s' in this context." % type_to_add)

        if type_to_add not in self.addable_types():
            raise ValueError("No content type called %s" % type_to_add)

        schema = CONTENT_SCHEMAS["Add%s" % type_to_add]()
        schema = schema.bind(context = self.context, request = self.request)
        form = Form(schema, buttons=(self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()

            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response

            name = appstruct['userid']
            del appstruct['userid']
            obj = CONTENT_TYPES[type_to_add](**appstruct)
            self.context[name] = obj

            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        self.response['form'] = form.render()
        return self.response

    @view_config(name='edit', context=IUser, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def edit_view(self):
        """ Edit user form """
        schema = CONTENT_SCHEMAS["Edit%s" % self.context.content_type]()
        schema = schema.bind(context = self.context, request = self.request)
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
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        appstruct = self.context.get_field_appstruct(schema)                
        self.response['form'] = form.render(appstruct)
        return self.response
        
    @view_config(name='change_password', context=IUser, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def change_password_view(self):
        """ Change password view. """
        schema = ChangePasswordSchema()
        schema = schema.bind(context = self.context, request = self.request)
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
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        self.response['form'] = form.render()
        return self.response
