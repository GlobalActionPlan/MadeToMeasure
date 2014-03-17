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
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.i18n import get_localizer
from deform import Button
from zope.component import createObject
from betahaus.pyracont.interfaces import IBaseFolder
from betahaus.pyracont.interfaces import IContentFactory
from betahaus.pyracont.factories import createSchema
from betahaus.viewcomponent import render_view_group
from pyramid_deform import FormView

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
from madetomeasure.interfaces import ITextSection
from madetomeasure.interfaces import IParticipant
from madetomeasure.interfaces import IParticipants
from madetomeasure.interfaces import IUsers
from madetomeasure.schemas.common import add_translations_node
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure import security
from madetomeasure.fanstaticlib import survey_managers_resources
from madetomeasure.fanstaticlib import survey_participants_resources


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
        self.response = {}
        if self.organisation:
            self.response['hex_color'] = self.organisation.get_field_value('hex_color')
            self.response['logo_link'] = self.organisation.get_field_value('logo_link')
        if self.userid:
            survey_managers_resources.need()
        else:
            survey_participants_resources.need()

    @reify
    def trans_util(self):
        return self.request.registry.getUtility(IQuestionTranslations)

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
    def survey(self):
        return find_interface(self.context, ISurvey)

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

    @reify
    def content_info(self):
        """ Return a dict with classes registered as a content factory. """
        return dict(self.request.registry.getUtilitiesFor(IContentFactory))

    @reify
    def addable_types(self):
        context_type = getattr(self.context, 'content_type', '')
        addable = []
        for (ctype, factory) in self.content_info.items():
            if context_type in factory._callable.allowed_contexts:
                if self.context_has_permission(self.context, "Add %s" % ctype):
                    addable.append(ctype)
        return addable

    def context_has_permission(self, context, permission):
        """ Check if a user has view permission on a specific context. """
        return security.context_has_permission(context, permission, self.userid)
    
    def context_has_schema(self, context, schema_name):
        """ Check if a schema is available named given schema + given context. """
        if hasattr(context, 'schemas'):
            return schema_name in context.schemas

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

    def set_lang(self, value):
        """ Set language cookie in response headers. They must still be passed to the view. Example:
            return HTTPFound(location = url, headers=self.request.response.headers)
        """
        self.request.response.set_cookie('_LOCALE_', value = value)

    def get_lang(self):
        return self.request.cookies.get('_LOCALE_', None)

    def render_view_group(self, group, context = None, **kw):
        context = context and context or self.context
        return render_view_group(context, self.request, group, view = self, **kw)    

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


class BaseForm(BaseView, FormView):
    default_success = _(u"Done")
    default_cancel = _(u"Canceled")

    button_login = Button('login', _(u"Login"))
    button_forgot_pw = Button('forgot_pw', _(u"Forgot password?"))
    button_save = Button('save', _(u"Save"))
    button_add = Button('add', _(u"Add"))
    button_send = Button('send', _(u"Send"))
    button_next = Button('next', _(u"Next"))
    button_previous = Button('previous', _(u"Previous"))
    button_cancel = Button('cancel', _(u"Cancel"))
    button_request = Button('request', _(u"Request"))
    button_change = Button('change', _(u"Change"))
    button_delete = Button('delete', _(u"Delete"))

    def get_bind_data(self):
        return {'context': self.context, 'request': self.request, 'view': self}

    def appstruct(self):
        if self.schema:
            return self.context.get_field_appstruct(self.schema)

    def cancel(self, *args):
        self.add_flash_message(self.default_cancel)
        return HTTPFound(location = self.request.resource_url(self.context))
    cancel_success = cancel_failure = cancel


@view_config(name="delete", renderer="templates/form.pt", permission=security.DELETE)
class DefaultDeleteForm(BaseForm):

    def __call__(self):
        if hasattr(self.context, 'check_safe_delete') and not self.context.check_safe_delete(self.request):
            #Abort - it's not safe to delete. Flash message will contain details from check_delete function
            return HTTPFound(location = self.request.resource_url(self.context))
        return super(DefaultDeleteForm, self).__call__()

    @property
    def buttons(self):
        return (self.button_delete, self.button_cancel,)

    @reify
    def schema(self):
        if 'delete' in self.context.schemas:
            return createSchema(self.context.schemas['delete'])

    def delete_success(self, appstruct):
        parent = self.context.__parent__
        del parent[self.context.__name__]
        self.add_flash_message(self.default_success)
        return HTTPFound(location = self.request.resource_url(parent))


@view_config(name="add", context = IBaseFolder, renderer = BASE_FORM_TEMPLATE)
class DefaultAddForm(BaseForm):

    @property
    def buttons(self):
        return (self.button_add, self.button_cancel,)

    @property
    def content_type(self):
        return self.request.GET.get('content_type', '')

    @reify
    def schema(self):
        schema = createSchema(self.factory._callable.schemas['add'])
        if self.content_type == 'SurveySection':
            self.trans_util.add_translations_schema(schema['heading_translations'], self.context)
            self.trans_util.add_translations_schema(schema['description_translations'], self.context, richtext=True)
        if self.content_type == 'Question':
            self.trans_util.add_translations_schema(schema['question_text'], self.context)
        if self.content_type == 'Choice':
            add_translations_node(schema, 'title_translations')
        if self.content_type == 'TextSection':
            add_translations_node(schema, 'title_translations', based_on = 'title')
            add_translations_node(schema, 'description_translations', based_on = 'description')
        return schema

    @reify
    def factory(self):
        return self.content_info[self.content_type]

    def __call__(self):
        if self.context_has_permission(self.context, "Add %s" % self.content_type):
            return super(DefaultAddForm, self).__call__()
        raise HTTPForbidden("Not allowed do add this content type")

    def add_success(self, appstruct):
        appstruct['creators'] = [self.userid]
        if appstruct.get('ignore_translations', None):
            if 'title_translations' in appstruct:
                del appstruct['title_translations']
        if self.content_type == 'User':
            name = appstruct['userid']
            del appstruct['userid']
            obj = self.factory(**appstruct)
        else: #All other
            obj = self.factory(**appstruct)
            if getattr(obj, 'uid_name', False):
                name = obj.uid
            else:
                name = obj.suggest_name(self.context)
        self.context[name] = obj
        url = self.request.resource_url(obj, getattr(obj, 'go_to_after_add', ''))
        self.add_flash_message(self.default_success)
        return HTTPFound(location = url)


@view_config(name = 'edit', context = IBaseFolder, renderer = BASE_FORM_TEMPLATE, permission = security.EDIT)
class DefaultEditForm(BaseForm):

    @property
    def buttons(self):
        return (self.button_save, self.button_cancel,)

    @reify
    def schema(self):
        schema = createSchema(self.context.schemas['edit'])
        #FIXME: Translations up for refactoring!
        if ISurvey.providedBy(self.context):
            self.trans_util.add_translations_schema(schema['heading_translations'], self.context)
        if ISurveySection.providedBy(self.context):
            self.trans_util.add_translations_schema(schema['heading_translations'], self.context)
            self.trans_util.add_translations_schema(schema['description_translations'], self.context, richtext=True)
        if IQuestion.providedBy(self.context):
            self.trans_util.add_translations_schema(schema['question_text'], self.context)
        if IChoice.providedBy(self.context):
            add_translations_node(schema, 'title_translations')
        if ITextSection.providedBy(self.context):
            add_translations_node(schema, 'title_translations', based_on = 'title')
            add_translations_node(schema, 'description_translations', based_on = 'description')
        return schema

    def save_success(self, appstruct):
        if appstruct.get('ignore_translations', None):
            if 'title_translations' in appstruct:
                del appstruct['title_translations']
        self.context.set_field_appstruct(appstruct)
        url = self.request.resource_url(self.context)
        self.add_flash_message(self.default_success)
        return HTTPFound(location = url)


class DefaultViews(BaseView):
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

    @view_config(context=IChoice)
    def redirect_to_parent_view(self):
        url = self.request.resource_url(self.context.__parent__)
        return HTTPFound(location = url)

    @view_config(name = 'select_lang', context = ISiteRoot, permission = NO_PERMISSION_REQUIRED)
    def select_lang_view(self):
        lang = self.request.GET.get('lang', None)
        msg = _(u"Language set to ${selected_lang}",
                mapping = {'selected_lang': self.trans_util.title_for_code(lang)})
        self.add_flash_message(msg)
        self.set_lang(lang)
        url = self.request.GET.get('return_url', self.request.resource_url(self.root))
        return HTTPFound(location = url, headers = self.request.response.headers)
