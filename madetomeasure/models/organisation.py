from BTrees.OOBTree import OOBTree
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import DENY_ALL
from zope.interface import implements

from betahaus.pyracont import BaseFolder
from madetomeasure.interfaces import IOrganisation
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure import security
from madetomeasure.models.security_aware import SecurityAware


class Organisation(BaseFolder, SecurityAware):
    implements(IOrganisation)
    content_type = 'Organisation'
    display_name = _(u"Organisation")
    allowed_contexts = ('SiteRoot',)
    
    __acl__ = [(Allow, security.ROLE_ADMIN, ALL_PERMISSIONS),
               (Allow, security.ROLE_ORGANISATION_MANAGER, ALL_PERMISSIONS),
               DENY_ALL,
              ]
    
    def __init__(self, data=None, **kwargs):
        """ Bootstrap an organisation """
        super(Organisation, self).__init__(data=data, **kwargs)
        #FIXME: Should be done by factories instead
        from madetomeasure.models.surveys import Surveys
        self['surveys'] = Surveys(title = _(u"Surveys"))

    @property
    def variants(self):
        if not hasattr(self, '__variants__'):
            self.__variants__ = OOBTree()
        return self.__variants__
        
    def get_variant(self, question_uid, lang):
        """ Returns variant of question for language if there is one """
        if question_uid in self.variants:
            if lang in self.variants[question_uid]:
                return self.variants[question_uid][lang]
            
        return None
        
    def set_variant(self, question_uid, lang, value):
        if not question_uid in self.variants:
            self.variants[question_uid] = {}
        self.variants[question_uid][lang] = value
