from zope.interface import implements

from madetomeasure.models.base import BaseFolder
from madetomeasure.interfaces import IOrganisation
from madetomeasure import MadeToMeasureTSF as _


class Organisation(BaseFolder):
    implements(IOrganisation)
    content_type = 'Organisation'
    display_name = _(u"Organisation")
    allowed_contexts = ('SiteRoot',)
    
    def __init__(self):
        """ Bootstrap an organisation """
        super(Organisation, self).__init__()
        
        #FIXME: Should be done by factories instead
        from madetomeasure.models.surveys import Surveys
        self['surveys'] = Surveys()
        
        from madetomeasure.models.questions import Questions
        self['questions'] = Questions()