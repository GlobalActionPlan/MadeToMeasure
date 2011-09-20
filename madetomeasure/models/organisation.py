from zope.interface import implements
from pyramid.renderers import render

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
    
    def get_logo_link(self):
        return getattr(self, '__logo_link__', '')
    
    def set_logo_link(self, value):
        self.__logo_link__ = value
        
    def get_hex_color(self):
        return getattr(self, '__hex_color__', '')

    def set_hex_color(self, value):
        self.__hex_color__ = value

    def render_dynamic_css(self, request):
        """ CSS based on settings in organisation.
            Should override a few of the basic styles.
        """
        response = {}
        response['hex_color'] = self.get_hex_color()
        response['logo_link'] = self.get_logo_link()
        return render('../views/templates/dynamic.css.pt', response, request=request)
