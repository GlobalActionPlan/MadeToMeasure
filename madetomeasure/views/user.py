from deform import Form
from deform.exception import ValidationFailure
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from betahaus.pyracont.factories import createSchema

from madetomeasure.interfaces import IUser
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_VIEW_TEMPLATE
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure import security


class UsersView(BaseView):

    @view_config(context=IUser, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    def admin_view(self):
        schema = createSchema(self.context.schemas['edit'])
        schema = schema.bind(context = self.context, request = self.request)
        appstruct = self.context.get_field_appstruct(schema)
        form = Form(schema, buttons=())
        self.response['form_resources'] = form.get_widget_resources()
        self.response['form'] = form.render(readonly = True, appstruct = appstruct)
        self.response['listing'] = self.listing_sniplet()
        return self.response
        
    @view_config(name='change_password', context=IUser, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def change_password_view(self):
        """ Change password view. """
        schema = createSchema(self.context.schemas['change_password'])
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
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)
        self.response['form'] = form.render()
        return self.response
