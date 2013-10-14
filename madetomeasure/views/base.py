from pyramid.decorator import reify
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
from pyramid.traversal import find_interface
from pyramid.renderers import get_renderer
from pyramid.renderers import render
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.i18n import get_locale_name
from pyramid.location import lineage
from pyramid.security import has_permission
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.i18n import get_localizer
from deform import Button
from deform import Form
from deform.exception import ValidationFailure
from zope.component import createObject
from betahaus.pyracont.interfaces import IBaseFolder
from betahaus.pyracont.interfaces import IContentFactory
from betahaus.pyracont.factories import createContent
from betahaus.pyracont.factories import createSchema

from madetomeasure.models.app import get_users_dt_helper
from madetomeasure.interfaces import IChoice
from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IQuestion
from madetomeasure.interfaces import IQuestionNode
from madetomeasure.interfaces import IQuestionTypes
from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure.interfaces import ISiteRoot
from madetomeasure.interfaces import ISurvey
from madetomeasure.interfaces import ISurveys
from madetomeasure.interfaces import ISurveySection
from madetomeasure.interfaces import IParticipant
from madetomeasure.interfaces import IParticipants
from madetomeasure.interfaces import IUsers
from madetomeasure.schemas.common import add_translations_node
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure import security


BASE_VIEW_TEMPLATE = 'templates/view.pt'
BASE_FORM_TEMPLATE = 'templates/form.pt'


class BaseView(object):

    def __init__(self, context, request):
        if isinstance(context, Exception):
            self.context = request.context
            self.exception = context
        else:
            self.context = context
            self.exception = None
        self.request = request
        self.response = dict(
            userid = self.userid,
            user = self.user_profile,
            main_macro = self.main_macro,
            root = self.root,
            addable_types = self.addable_types,
            content_info = self.content_info,
            flash_messages = self.get_flash_messages,
            organisation = self.organisation,
            survey_dt = self.survey_dt,
            user_dt = self.user_dt,
            listing_sniplet = self.listing_sniplet,
            context_has_permission = self.context_has_permission,
            context_has_schema = self.context_has_schema,
            path = self.path,
            exception = self.exception,
        )
        if self.organisation:
            self.response['hex_color'] = self.organisation.get_field_value('hex_color')
            self.response['logo_link'] = self.organisation.get_field_value('logo_link')

        self.trans_util = self.request.registry.getUtility(IQuestionTranslations)

    @reify
    def path(self):
        try:
            path = [x for x in lineage(self.context)]
            path.reverse()
            return tuple(path)
        except:
            return ()

    @reify
    def localizer(self):
        return get_localizer(self.request)

    @reify
    def userid(self):
        return authenticated_userid(self.request)

    @reify
    def user_profile(self):
        if self.userid is None or self.root is None:
            return
        return self.root['users'].get(self.userid)

    @reify
    def root(self):
        try:
            return find_root(self.context)
        except AttributeError:
            return None
    
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

    @reify
    def user_dt(self):
        if not self.userid:
            return None
        return get_users_dt_helper(request = self.request)

    def context_has_permission(self, context, permission):
        """ Check if a user has view permission on a specific context. """
        return security.context_has_permission(context, permission, self.userid)

    def context_has_schema(self, context, schema_name):
        """ Check if a schema is available named given schema + given context. """
        if hasattr(context, 'schemas'):
            return schema_name in context.schemas

    @reify
    def content_info(self):
        """ Return a dict with classes registered as a content factory. """
        return dict(self.request.registry.getUtilitiesFor(IContentFactory))

    @reify
    def addable_types(self):
        context_type = getattr(self.context, 'content_type', '')
        addable = []
        for (type, factory) in self.content_info.items():
            if context_type in factory._callable.allowed_contexts:
                if self.context_has_permission(self.context, "Add %s" % type):
                    addable.append(type)
        return addable

    def question_types_info(self):
        results = {}
        for (name, factory) in self.content_info:
            if IQuestionNode.providedBy(factory):
                results[name] = factory
        return results

    def listing_sniplet(self, contents=None, display_type = False):
        response = {}
        if contents is None:
            response['contents'] = [x for x in self.context.values() if security.context_has_permission(x, security.VIEW, self.userid)]
        else:
            response['contents'] = contents
        response['context_has_permission'] = self.context_has_permission
        response['display_type'] = display_type
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
        buttons['delete'] = Button('delete', _(u"Delete"))
        return buttons

    @view_config(context=IUsers, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    @view_config(context=ISurveys, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    @view_config(context=IParticipant, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    @view_config(context=IParticipants, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    def admin_listing_view(self):
        #FIXME: move when implemented
        self.response['listing'] = self.listing_sniplet()
        return self.response

    @view_config(context=IQuestionTypes, renderer=BASE_VIEW_TEMPLATE, permission=security.VIEW)
    def question_type_listing(self):
        self.response['listing'] = self.listing_sniplet(display_type = True)
        return self.response

    @view_config(context=ISiteRoot, renderer="templates/root_view.pt", permission = NO_PERMISSION_REQUIRED)
    def root_view(self):
        contents = []
        for obj in self.context.values():
            if IOrganisation.providedBy(obj) and security.context_has_permission(obj, security.VIEW, self.userid):
                contents.append(obj)
        contents = sorted(contents, key = lambda x: x.title.lower())
        self.response['listing'] = self.listing_sniplet(contents)
        return self.response

    @view_config(name="delete", renderer="templates/form.pt", permission=security.DELETE)
    def delete_form(self):
        """ This form is a generic delete form. It's up to the delete schema (which must exist to use this)
            whether it must have some sort of validation.
        """
        if hasattr(self.context, 'check_safe_delete') and not self.context.check_safe_delete(self.request):
            #Abort - it's not safe to delete. Flash message will contain details from check_delete function
            return HTTPFound(location = self.request.resource_url(self.context))
        schema = createSchema(self.context.schemas['delete'])
        schema = schema.bind(context = self.context, request = self.request)
        form = Form(schema, buttons=(self.buttons['delete'], self.buttons['cancel'], ))
        self.response['form_resources'] = form.get_widget_resources()
        if self.request.method == 'POST':
            parent = self.context.__parent__
            if 'delete' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    form.validate(controls)
                except ValidationFailure, e:
                    self.response['form'] = e.render()
                    return self.response
                del parent[self.context.__name__]
                self.add_flash_message(_(u"Deleted"))
            if 'cancel' in self.request.POST:
                self.add_flash_message(_(u"Canceled"))
            return HTTPFound(location = self.request.resource_url(parent))
        self.response['form'] = form.render()
        return self.response

    @view_config(name = 'add', context = IBaseFolder, renderer = BASE_FORM_TEMPLATE)
    def add_view(self):
        """ Generic add view.
        """
        type_to_add = self.request.GET.get('content_type')

        #Permission check
        add_permission = "Add %s" % type_to_add #FIXME: Refactor, put on content type?
        if not has_permission(add_permission, self.context, self.request):
            raise HTTPForbidden("You're not allowed to add '%s' in this context." % type_to_add)

        if 'cancel' in self.request.POST:
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)
        
        if type_to_add not in self.addable_types:
            raise ValueError("No content type called %s addable here" % type_to_add)

        schema = createSchema(self.content_info[type_to_add]._callable.schemas['add'])
        schema = schema.bind(context=self.context, request=self.request)

        #FIXME: Need better way of determining ways of adding fields to schema. After bind?
        if type_to_add == 'SurveySection':
            self.trans_util.add_translations_schema(schema['heading_translations'], self.context)
            self.trans_util.add_translations_schema(schema['description_translations'], self.context, richtext=True)
        if type_to_add == 'Question':
            self.trans_util.add_translations_schema(schema['question_text'], self.context)
        if type_to_add == 'Choice':
            add_translations_node(schema, 'title_translations')

        form = Form(schema, buttons=(self.buttons['save'], self.buttons['cancel'], ))
        self.response['form_resources'] = form.get_widget_resources()
        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            appstruct['creators'] = [self.userid]
            if appstruct.get('ignore_translations', None):
                if 'title_translations' in appstruct:
                    del appstruct['title_translations']
            if type_to_add == 'User':
                name = appstruct['userid']
                del appstruct['userid']
                obj = createContent(type_to_add, **appstruct)
            else: #All other
                obj = createContent(type_to_add, **appstruct)
                if getattr(obj, 'uid_name', False):
                    name = obj.uid
                else:
                    name = obj.suggest_name(self.context)
            self.context[name] = obj
            url = self.request.resource_url(obj, getattr(obj, 'go_to_after_add', ''))
            return HTTPFound(location = url)
        self.response['form'] = form.render()
        return self.response

    @view_config(name = 'edit', context = IBaseFolder, renderer = BASE_FORM_TEMPLATE, permission = security.EDIT)
    def edit_view(self):
        """ Generic edit view
        """
        if 'cancel' in self.request.POST:
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)
        schema = createSchema(self.context.schemas['edit'])
        schema = schema.bind(context = self.context, request = self.request)

        if ISurvey.providedBy(self.context):
            self.trans_util.add_translations_schema(schema['heading_translations'], self.context)
        if ISurveySection.providedBy(self.context):
            self.trans_util.add_translations_schema(schema['heading_translations'], self.context)
            self.trans_util.add_translations_schema(schema['description_translations'], self.context, richtext=True)
        if IQuestion.providedBy(self.context):
            self.trans_util.add_translations_schema(schema['question_text'], self.context)
        if IChoice.providedBy(self.context):
            add_translations_node(schema, 'title_translations')

        form = Form(schema, buttons=(self.buttons['save'], self.buttons['cancel'], ))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            if appstruct.get('ignore_translations', None):
                if 'title_translations' in appstruct:
                    del appstruct['title_translations']
            self.context.set_field_appstruct(appstruct)
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)
        appstruct = self.context.get_field_appstruct(schema)
        self.response['form'] = form.render(appstruct)
        return self.response

    @view_config(context=IChoice)
    def redirect_to_parent_view(self):
        url = self.request.resource_url(self.context.__parent__)
        return HTTPFound(location = url)
