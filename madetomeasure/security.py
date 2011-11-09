from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy

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

#Add permissions
#Note: For add permissions, check each content types class
ADD_QUESTION = 'Add Question'
ADD_USER = 'Add User'
ADD_ORGANISATION = 'Add Organisation'
ADD_SURVEY = 'Add Survey'
ADD_SURVEY_SECTION = 'Add SurveySection'

ROOT_ROLES = ((ROLE_ADMIN, _(u'Administrator')),)
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
