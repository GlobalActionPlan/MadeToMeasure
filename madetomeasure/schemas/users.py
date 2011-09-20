import colander
import deform

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.common import time_zone_node


def password_validation(node, value):
    """ check that password is
        - at least 6 chars and at most 100.
    """
    if len(value) < 6:
        raise colander.Invalid(node, _(u"Too short. At least 6 chars required."))
    if len(value) > 100:
        raise colander.Invalid(node, _(u"Less than 100 chars please."))


class AddUserSchema(colander.Schema):
    userid = colander.SchemaNode(colander.String(),
                                 title=_(u"Userid"),
                                 validator=colander.Length(min=2, max=10),)
    password = colander.SchemaNode(colander.String(),
                                   title=_('Password'),
                                   validator=password_validation,
                                   widget=deform.widget.CheckedPasswordWidget(size=20),)
    first_name = colander.SchemaNode(colander.String(),
                                     title=_(u"First name"),)
    last_name = colander.SchemaNode(colander.String(),
                                    title=_(u"Last name"),)
    email = colander.SchemaNode(colander.String(),
                                title=_(u"Email"),
                                missing=u"",
                                validator=colander.Email(),)
    time_zone = time_zone_node()


class EditUserSchema(colander.Schema):
    first_name = colander.SchemaNode(colander.String(),
                                     title=_(u"First name"),)
    last_name = colander.SchemaNode(colander.String(),
                                    title=_(u"Last name"),)
    email = colander.SchemaNode(colander.String(),
                                title=_(u"Email"),
                                missing=u"",
                                validator=colander.Email(),)
    time_zone = time_zone_node()


class ChangePasswordSchema(colander.Schema):
    password = colander.SchemaNode(colander.String(),
                                   title=_('Password'),
                                   validator=password_validation,
                                   widget=deform.widget.CheckedPasswordWidget(size=20),)
