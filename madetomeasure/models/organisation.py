from pyramid.renderers import render
from pyramid.security import Allow, Everyone, ALL_PERMISSIONS
from pyramid.security import DENY_ALL
from zope.interface import implements

from madetomeasure.models.base import BaseFolder
from madetomeasure.interfaces import IOrganisation
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure import security


class Organisation(BaseFolder):
    implements(IOrganisation)
    content_type = 'Organisation'
    display_name = _(u"Organisation")
    allowed_contexts = ('SiteRoot',)
    
    __acl__ = [(Allow, security.ROLE_ADMIN, ALL_PERMISSIONS),
               (Allow, security.ROLE_ORGANISATION_MANAGER, ALL_PERMISSIONS),
               DENY_ALL,
              ]
    
    def __init__(self):
        """ Bootstrap an organisation """
        super(Organisation, self).__init__()
        
        #FIXME: Should be done by factories instead
        from madetomeasure.models.surveys import Surveys
        self['surveys'] = Surveys()
        
        from madetomeasure.models.questions import Questions
        self['questions'] = Questions()
    
    def get_logo_link(self):
        return getattr(self, '__logo_link__', '')
    
    def set_logo_link(self, value):
        self.__logo_link__ = value
        
    def get_hex_color(self):
        return getattr(self, '__hex_color__', '')

    def set_hex_color(self, value):
        self.__hex_color__ = value
