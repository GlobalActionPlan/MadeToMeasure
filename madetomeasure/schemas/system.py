import colander
import deform

from pyramid.traversal import find_root
from betahaus.pyracont.decorators import schema_factory

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.users import password_validation
from madetomeasure.schemas.validators import deferred_userid_or_email_validation
from madetomeasure import security


@colander.deferred
def deferred_came_from(node, kw):
    return kw.get('came_from', u'')


@schema_factory()
class LoginSchema(colander.Schema):
    userid_or_email = colander.SchemaNode(colander.String(),
                                          title = _(u"UserID or email address."),
                                          validator = deferred_userid_or_email_validation,)
    password = colander.SchemaNode(colander.String(),
                                   title=_('Password'),
                                   widget=deform.widget.PasswordWidget(size=20),)
    came_from = colander.SchemaNode(colander.String(),
                                    widget = deform.widget.HiddenWidget(),
                                    missing='',
                                    default=deferred_came_from,)


@schema_factory()
class RequestPasswordSchema(colander.Schema):
    userid_or_email = colander.SchemaNode(colander.String(),
                                          title = _(u"UserID or email address."),
                                          validator = deferred_userid_or_email_validation,)

@schema_factory()
class TokenPasswordChange(colander.Schema):
    password = colander.SchemaNode(colander.String(),
                                   validator=password_validation,
                                   widget=deform.widget.CheckedPasswordWidget(size=20),
                                   title=_('Password'))


@colander.deferred
def deferred_user_choices_widget(node, kw):
    context = kw['context']
    root = find_root(context)
    user_choices = tuple(root['users'].keys())
    return deform.widget.AutocompleteInputWidget(size=20,
                                                 values = user_choices,
                                                 min_length=1)

@colander.deferred
def deferred_role_choices_widget(node, kw):
    context = kw['context']
    root = find_root(context)
    if context is root:
        #Only show administrator as selectable group in root
        group_choices = security.ROOT_ROLES
    else:
        #In other contexts (like Organisation) meeting roles apply
        group_choices = security.ORGANISATION_ROLES
    return deform.widget.CheckboxChoiceWidget(values = group_choices,
                                              missing = colander.null)


class UserIDAndGroupsSchema(colander.Schema):
    userid = colander.SchemaNode(
        colander.String(),
        widget = deferred_user_choices_widget,
        )
    groups = colander.SchemaNode(
        deform.Set(allow_empty = True),
        title = _(u"Role"),
        widget=deferred_role_choices_widget,
        )


class UserIDsAndGroupsSequenceSchema(colander.SequenceSchema):
    userid_and_groups = UserIDAndGroupsSchema(title=_(u'Roles for user'),)

@schema_factory()
class PermissionsSchema(colander.Schema):
    userids_and_groups = UserIDsAndGroupsSequenceSchema(title=_(u'Role settings for users'))


@schema_factory()
class RenameSchema(colander.Schema):
    """ Rename object schema """
    #FIXME: Needs validation etc
    name = colander.SchemaNode(colander.String(),
                               title = _(u"rename_schema_name_description",
                                         default = u"New name, must be unique in this context and can only contain 'a-z' and '-'."),)
