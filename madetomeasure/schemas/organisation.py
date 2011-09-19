import re

import colander
import deform

from madetomeasure import MadeToMeasureTSF as _


HEX_COLOR = re.compile("^#[0-9a-f]{6}$", re.IGNORECASE)
LOGO_LINK = re.compile("^http\:\/\/(.*)(gif|png|jpg|jpeg)$", re.IGNORECASE)


class OrganisationSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _(u"Organisation name"),)
    logo_link = colander.SchemaNode(colander.String(),
                                    title = _(u"Logo link"),
                                    description = _(u"Must be a HTTP link to a Gif, Jpeg och Png file."),
                                    validator = colander.Regex(LOGO_LINK),
                                    missing=u"",)
    hex_color = colander.SchemaNode(colander.String(),
                                    title = _(u"Color value"),
                                    description = _(u"Must be a hex rgb value, same as all websites. Example: '#FF0000' for red."),
                                    validator = colander.Regex(HEX_COLOR),
                                    missing=u"",)
