from pyramid.decorator import reify
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
from pyramid.traversal import find_interface
from pyramid.url import resource_url
from pyramid.renderers import get_renderer, render
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from deform import Button
from deform import Form
from colander import Schema
from deform.exception import ValidationFailure
from zope.component import createObject
from pyramid.i18n import get_locale_name
from pyramid.location import lineage
from pyramid.security import has_permission

from madetomeasure.models.app import generate_slug
from madetomeasure.models.app import get_users_dt_helper
from madetomeasure.interfaces import *
from madetomeasure.schemas import LoginSchema, CONTENT_SCHEMAS
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.models import CONTENT_TYPES
from madetomeasure import security


BASE_VIEW_TEMPLATE = 'templates/view.pt'
BASE_FORM_TEMPLATE = 'templates/form.pt'


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        path = [x for x in lineage(self.context)]
        path.reverse()
        self.response = dict(
            userid = self.userid,
            user = self.user_profile,
            main_macro = self.main_macro,
            resource_url = resource_url,
            root = self.root,
            addable_types = self.addable_types(),
            flash_messages = self.get_flash_messages,
            organisation = self.organisation,
            survey_dt = self.survey_dt,
            user_dt = None,
            path = tuple(path),
            footer_html = self.root.get_footer_html(),
            listing_sniplet = self.listing_sniplet,
            confirm_previous = _("If you go back, the changes made here will be permanently lost."),
        )
        if self.userid:
            self.response['user_dt'] = get_users_dt_helper(request=request)
        if self.organisation:
            self.response['hex_color'] = self.organisation.get_hex_color()
            self.response['logo_link'] = self.organisation.get_logo_link()

        self.trans_util = self.request.registry.getUtility(IQuestionTranslations)

    @reify
    def userid(self):
        return authenticated_userid(self.request)

    @reify
    def user_profile(self):
        if self.userid is None:
            return
        return self.root['users'].get(self.userid)

    @reify
    def root(self):
        return find_root(self.context)
    
    @reify
    def organisation(self):
        return find_interface(self.context, IOrganisation)

    @reify
    def main_macro(self):
        return get_renderer('templates/main.pt').implementation().macros['master']
        
    def get_flash_messages(self):
        for message in self.request.session.pop_flash():
            yield message
    
    def add_flash_message(self, message):
        self.request.session.flash(message)

    @reify
    def survey_dt(self):
        survey = find_interface(self.context, ISurvey)
        if not survey:
            return
        tz = survey.get_time_zone()
        loc = get_locale_name(self.request)
        return createObject('dt_helper', tz, loc)

    def addable_types(self):
        #FIXME: Check permission?
        context_type = getattr(self.context, 'content_type', '')
        addable = []
        for (type, klass) in CONTENT_TYPES.items():
            if context_type in klass.allowed_contexts:
                addable.append(type)
        return addable

    def listing_sniplet(self, contents=None):
        response = {}
        response['resource_url'] = resource_url
        if contents is None:
            response['contents'] = self.context.values()
        else:
            response['contents'] = contents
            
        return render('templates/sniplets/listing.pt', response, request=self.request)

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

    @view_config(context=ISiteRoot, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    @view_config(context=IUsers, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    @view_config(context=ISurveys, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    @view_config(context=IParticipant, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    @view_config(context=IParticipants, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    @view_config(context=IOrganisation, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    def admin_listing_view(self):
        #FIXME: move when implemented
        return self.response

    @view_config(name="delete", renderer="templates/form.pt", permission=security.DELETE)
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
        type_to_add = self.request.GET.get('content_type')

        #Permission check
        add_permission = "Add %s" % type_to_add
        if not has_permission(add_permission, self.context, self.request):
            raise Forbidden("You're not allowed to add '%s' in this context." % content_type)

        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)
        
        if type_to_add not in self.addable_types():
            raise ValueError("No content type called %s" % type_to_add)

        schema = CONTENT_SCHEMAS["Add%s" % type_to_add]()
        schema = schema.bind()

        #FIXME: Need better way of determining ways of adding fields to schema. After bind?
        if type_to_add == 'SurveySection':
            self.context.add_structured_question_choices(schema['structured_question_ids'])
            self.trans_util.add_translations_schema(schema['heading_translations'])

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
            
            name = generate_slug(self.context, appstruct['title'])
            self.context[name] = obj
    
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        self.response['form'] = form.render()
        return self.response


    @view_config(name='edit', context=ISiteRoot, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    @view_config(name='edit', context=ISurvey, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    @view_config(name='edit', context=ISurveySection, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    @view_config(name='edit', context=IOrganisation, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    @view_config(name='edit', context=IParticipant, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def edit_view(self):
        """ Generic edit view when accessors and mutators match get_ and set_ methods
            on the model.
        """

        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        schema = CONTENT_SCHEMAS["Edit%s" % self.context.content_type]()
        schema = schema.bind(context = self.context,)
        
        if ISurveySection.providedBy(self.context):
            self.context.__parent__.add_structured_question_choices(schema['structured_question_ids'])
            self.trans_util.add_translations_schema(schema['heading_translations'])

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
                value = accessor()
                if value is not None:
                    appstruct[field.name] = accessor()

        self.response['form'] = form.render(appstruct)
        return self.response
    
