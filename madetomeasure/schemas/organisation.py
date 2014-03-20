import re

import colander
from betahaus.pyracont.decorators import schema_factory

from madetomeasure import MadeToMeasureTSF as _


HEX_COLOR = re.compile(r"^#[0-9a-f]{6}$", re.IGNORECASE)
LOGO_LINK = re.compile(r"^http\:\/\/(.*)(gif|png|jpg|jpeg)$", re.IGNORECASE)


@schema_factory('OrganisationSchema')
class OrganisationSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _(u"Organisation name"),)
    logo_link = colander.SchemaNode(colander.String(),
                                    title = _(u"Logo link"),
                                    description = _(u"logo_link_description_text",
                                                    default = u"Must be a HTTP link to a Gif, Jpeg och Png file. Max width/height: 50/300 px."),
                                    validator = colander.Regex(LOGO_LINK),
                                    missing=u"",)
