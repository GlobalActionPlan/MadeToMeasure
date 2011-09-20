from zope.interface import implements

from madetomeasure.models.base import BaseFolder
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *


class SiteRoot(BaseFolder):
    implements(ISiteRoot)
    content_type = 'SiteRoot'
    display_name = _(u"Site root")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name

    def set_title(self, value):
        pass
    
    def get_footer_html(self):
        return getattr(self, '__footer_html__', u'')
    
    def set_footer_html(self, value):
        self.__footer_html__ = value
