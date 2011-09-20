import colander
import deform

from madetomeasure import MadeToMeasureTSF as _


class EditParticipant(colander.Schema):
    email = colander.SchemaNode(colander.String(),
                                title=_(u"Change email address"),
                                validator=colander.Email(),)
    