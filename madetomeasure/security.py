from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Authenticated
from pyramid.security import Everyone
from pyramid.threadlocal import get_current_registry

from madetomeasure import MadeToMeasureTSF as _


#Roles, which are the same as groups really
ROLE_ADMIN = 'role:Admin'
ROLE_ORGANISATION_MANAGER = 'role:OrganisationManager'
ROLE_TRANSLATOR = 'role:Translator'

#Global Permissions
VIEW = 'View'
EDIT = 'Edit'
DELETE = 'Delete'
TRANSLATE = 'Translate'
MANAGE_SURVEY = 'Manage survey'
MANAGE_SERVER = 'Manage server'
MANAGE_ORGANISATION = 'Manage organisation'

#Add permissions
ADD_QUESTION = 'Add Question'
ADD_USER = 'Add User'
ADD_ORGANISATION = 'Add Organisation'
ADD_SURVEY = 'Add Survey'
ADD_SURVEY_SECTION = 'Add SurveySection'

ROOT_ROLES = ((ROLE_ADMIN, _(u'Administrator')),
              (ROLE_TRANSLATOR, _(u"Translator")),)
ORGANISATION_ROLES = ((ROLE_ORGANISATION_MANAGER, _(u'Organisation manager')),)

def groupfinder(name, request):
    """ Get groups for the current user.
        This is also a callback for the Authorization policy.
    """
    return request.context.get_groups(name)

#Authentication policies
authn_policy = AuthTktAuthenticationPolicy(secret='sosecret',
                                           callback=groupfinder)
authz_policy = ACLAuthorizationPolicy()

def context_has_permission(context, permission, userid):
    """ Special permission check that is agnostic of the request.context attribute.
        (As opposed to pyramid.security.has_permission)
        Don't use anything else than this one to determine permissions for something
        where the request.context isn't the same as context, for instance another 
        object that appears in a listing.
    """
    principals = context_effective_principals(context, userid)
    reg = get_current_registry()
    authz_policy = reg.getUtility(IAuthorizationPolicy)
    return authz_policy.permits(context, principals, permission)

def context_effective_principals(context, userid):
    """ Special version of pyramid.security.effective_principals that
        adds groups based on context instead of request.context
        
        A note about Authenticated: It doesn't mean that the current user is authenticated,
        rather than someone with a userid are part of the Authenticated group, since by using
        a userid they will have logged in :)
    """
    effective_principals = [Everyone]
    if userid is None:
        return effective_principals
    groups = context.get_groups(userid)
    effective_principals.append(Authenticated)
    effective_principals.append(userid)
    effective_principals.extend(groups)
    return effective_principals
