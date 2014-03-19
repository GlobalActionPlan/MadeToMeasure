from betahaus.viewcomponent import view_action
from pyramid.traversal import find_resource
from pyramid.renderers import render

from madetomeasure import security
from madetomeasure import MadeToMeasureTSF as _


def _render_default_menu(context, request, va, **kw):
    view = kw['view']
    context_path = va.kwargs.get('context_path', None)
    context = context_path and find_resource(context, context_path) or context
    context_perm = va.kwargs.get('context_perm', None)
    if context_perm and not view.context_has_permission(context, context_perm):
        return
    view_name = va.kwargs.get('view_name', '')
    url = request.resource_url(context, view_name)
    response = dict(context = context, va = va, view = view, url = url)
    return render("madetomeasure:views/templates/sniplets/menu_item.pt", response, request = request)


@view_action('global_menu', 'participants', title = _(u"Participants"),
             context_path = 'participants', context_perm = security.VIEW)
@view_action('global_menu', 'questions', title = _(u"Questions"),
             context_path = 'questions', context_perm = security.VIEW)
@view_action('global_menu', 'question_types', title = _(u"Question types"),
             context_path = 'question_types', context_perm = security.VIEW)
@view_action('global_menu', 'users', title = _(u"Users"),
             context_path = 'users', context_perm = security.VIEW)
@view_action('global_menu', 'permissions', title = _(u"Global permissions"),
             context_perm = security.MANAGE_SERVER, view_name = 'permissions')
def generic_root_menu_item(context, request, va, **kw):
    """ Must be called with root as context. """
    assert context.content_type == 'SiteRoot' #Just to avoid silly bugs
    return _render_default_menu(context, request, va, **kw)


@view_action('organisation_menu', 'participants', title = _(u"Permissions"),
             context_perm = security.MANAGE_ORGANISATION, view_name = 'permissions')
@view_action('organisation_menu', 'variants', title = _(u"Question variants"),
             context_perm = security.EDIT, view_name = 'variants')
def generic_organisation_menu_item(context, request, va, **kw):
    """ Must be called with organisation as context. """
    assert context.content_type == 'Organisation' #Just to avoid silly bugs
    return _render_default_menu(context, request, va, **kw)


@view_action('survey_menu', 'view', title = _(u"View"),
             context_perm = security.VIEW, priority = 1)
@view_action('survey_menu', 'invitation_emails', title = _(u"Invitations"),
             context_perm = security.MANAGE_SURVEY, view_name = 'invitation_emails')
@view_action('survey_menu', 'participants', title = _(u"Participants"),
             context_perm = security.MANAGE_SURVEY, view_name = 'participants')
@view_action('survey_menu', 'results', title = _(u"Results"),
             context_perm = security.MANAGE_SURVEY, view_name = 'results')
@view_action('survey_menu', 'reorder_sections', title = _(u"Reorder sections"),
             context_perm = security.MANAGE_SURVEY, view_name = 'reorder')
@view_action('survey_menu', 'manage_questions', title = _(u"Manage questions"),
             context_perm = security.MANAGE_SURVEY, view_name = 'manage_questions')
@view_action('survey_menu', 'export', title = _(u"Export"),
             context_perm = security.MANAGE_SURVEY, view_name = 'export.csv')
@view_action('survey_menu', 'clone', title = _(u"Clone"),
             context_perm = security.MANAGE_SURVEY, view_name = 'clone')
def generic_survey_menu_item(context, request, va, **kw):
    """ Must be called with survey as context. """
    assert context.content_type == 'Survey' #Just to avoid silly bugs
    return _render_default_menu(context, request, va, **kw)

@view_action('context_menu', 'add', title = _(u"Add"), priority = 1)
def add_context_tab(context, request, va, **kw):
    """ This is the dropdown add tab. Permissions are for each addable content type. """
    view = kw['view']
    response = dict(context = context, va = va, view = view)
    return render("madetomeasure:views/templates/sniplets/add_content_tab.pt", response, request = request)

@view_action('context_menu', 'edit', title = _(u"Edit"), priority = 2,
             permission = security.EDIT, schema_name = 'edit', view_name = 'edit',
             icon = 'pencil')
@view_action('context_menu', 'delete', title = _(u"Delete"), priority = 5,
             permission = security.DELETE, schema_name = 'delete', view_name = 'delete',
             icon = 'remove')
#FIXME: Translations!
def generic_context_tabs(context, request, va, **kw):
    """ Actions for a specific context. """
    schema_name = va.kwargs.get('schema_name', None)
    if schema_name and schema_name not in context.schemas:
        return
    view = kw['view']
    view_name = va.kwargs.get('view_name', '')
    icon = va.kwargs.get('icon', None)
    url = request.resource_url(context, view_name)
    response = dict(context = context,
                    va = va,
                    view = view,
                    url = url,
                    icon = icon,
                    active = request.view_name == view_name,)
    return render("madetomeasure:views/templates/sniplets/context_tab.pt", response, request = request)
