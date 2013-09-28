from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Authenticated
from pyramid.security import DENY_ALL
from zope.interface import implements
from betahaus.pyracont import BaseFolder

from madetomeasure import security
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import ISiteRoot
from madetomeasure.models.security_aware import SecurityAware


class SiteRoot(BaseFolder, SecurityAware):
    implements(ISiteRoot)
    content_type = 'SiteRoot'
    display_name = _(u"Site root")
    allowed_contexts = () #Not manually addable
    schemas = {'edit': 'EditSiteRoot'}

    __acl__ = [(Allow, security.ROLE_ADMIN, ALL_PERMISSIONS),
               (Allow, Authenticated, security.VIEW),
               DENY_ALL]
