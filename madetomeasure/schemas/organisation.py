import colander
import deform

from madetomeasure import MadeToMeasureTSF as _


class OrganisationSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _(u"Organisation name"),)
