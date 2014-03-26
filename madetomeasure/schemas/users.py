import colander
import deform
from betahaus.pyracont.decorators import schema_factory
from pyramid.traversal import find_root

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
    return colander.SchemaNode(colander.Set(),
                               title = _(u"I am a translator and translate to the following languages"),
                               description = _(u"You will need the translator permission to actually translate."),
                               widget = deferred_translator_languages_widget,
                               missing=(),
                               )

def datetime_loc_node():
    return colander.SchemaNode(colander.String(),
                               title = _(u"Datetime localisation"),
                               description = _(u"Pick localisation for date format for this user."),
                               widget = deferred_pick_language_widget,
                               missing = 'en',
                               default = 'en')


@colander.deferred
def deferred_new_userid_validator(node, kw):
    context = kw['context']
    return NewUserIDValidator(context)


class NewUserIDValidator(object):

    def __init__(self, context):
        self.context = context

    def __call__(self, node, value):
        #FIXME: Proper regexp validator of chars
        if len(value) < 2:
            raise colander.Invalid(node, _(u"Too short"))
        if len(value) > 50:
            raise colander.Invalid(node, _(u"Too long"))
        root = find_root(self.context)
        if value in root['users'].keys():
            raise colander.Invalid(node, _(u"Already exists"))


@schema_factory('AddUserSchema')
class AddUserSchema(colander.Schema):
    userid = colander.SchemaNode(colander.String(),
                                 title=_(u"UserID"),
                                 validator = deferred_new_userid_validator)
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


@schema_factory('EditUserSchema')
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


@schema_factory('ChangePasswordSchema')
class ChangePasswordSchema(colander.Schema):
    password = colander.SchemaNode(colander.String(),
                                   title=_('Password'),
                                   validator=password_validation,
                                   widget=deform.widget.CheckedPasswordWidget(size=20),)
