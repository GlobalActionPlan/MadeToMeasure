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


from madetomeasure.interfaces import *
from madetomeasure.schemas import LoginSchema, CONTENT_SCHEMAS
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.models import CONTENT_TYPES


BASE_VIEW_TEMPLATE = 'templates/view.pt'

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
    @view_config(context=IQuestions, renderer=BASE_VIEW_TEMPLATE)
    def admin_listing_view(self):
        #FIXME: move when implemented
        return self.response

    @view_config(context=IQuestion, renderer=BASE_VIEW_TEMPLATE)
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
