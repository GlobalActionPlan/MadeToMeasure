import colander
import deform

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.common import time_zone_node
from madetomeasure.schemas.common import deferred_translator_languages_widget
from madetomeasure.schemas.common import deferred_pick_language_widget

def password_validation(node, value):
    """ check that password is
        - at least 6 chars and at most 100.
    """
    if len(value) < 6:
        raise colander.Invalid(node, _(u"Too short. At least 6 chars required."))
    if len(value) > 100:
        raise colander.Invalid(node, _(u"Less than 100 chars please."))

def translator_node():
    return colander.SchemaNode(deform.Set(allow_empty = True),
                               title = _(u"I am a translator and translate to the following languages"),
                               description = _(u"You will need the translator permission to actually translate."),
                               widget = deferred_translator_languages_widget,
                               missing=(),
                               )

def datetime_loc_node():
    return colander.SchemaNode(colander.String(),
                               title = _(u"Datetime localisation"),
                               description = _(u"Pick locasitaion for date format for this user."),
                               widget = deferred_pick_language_widget,
                               missing = 'en',
                               default = 'en')

class AddUserSchema(colander.Schema):
    userid = colander.SchemaNode(colander.String(),
                                 title=_(u"UserID"),
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
                                validator=colander.Email(),)
    time_zone = time_zone_node()
    datetime_localisation = datetime_loc_node()
    translator_langs = translator_node()



class EditUserSchema(colander.Schema):
    first_name = colander.SchemaNode(colander.String(),
                                     title=_(u"First name"),)
    last_name = colander.SchemaNode(colander.String(),
                                    title=_(u"Last name"),)
    email = colander.SchemaNode(colander.String(),
                                title=_(u"Email"),
                                validator=colander.Email(),)
    time_zone = time_zone_node()
    datetime_localisation = datetime_loc_node()
    translator_langs = translator_node()


class ChangePasswordSchema(colander.Schema):
    password = colander.SchemaNode(colander.String(),
                                   title=_('Password'),
                                   validator=password_validation,
                                   widget=deform.widget.CheckedPasswordWidget(size=20),)
