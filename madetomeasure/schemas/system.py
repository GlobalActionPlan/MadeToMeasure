import colander
import deform

from pyramid.traversal import find_root

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.users import password_validation
from madetomeasure import security


@colander.deferred
def deferred_came_from(node, kw):
    return kw.get('came_from', u'')


class LoginSchema(colander.Schema):
    userid = colander.SchemaNode(colander.String(),
                                 title=_(u"UserID"))
    password = colander.SchemaNode(colander.String(),
                                   title=_('Password'),
                                   widget=deform.widget.PasswordWidget(size=20),)
    came_from = colander.SchemaNode(colander.String(),
                                    widget = deform.widget.HiddenWidget(),
                                    missing='',
                                    default=deferred_came_from,)


class RequestPasswordSchema(colander.Schema):
    userid_or_email = colander.SchemaNode(colander.String(),
                                          title = _(u"UserID or email address."))


def TokenPasswordChange(context):
    class _schema(colander.Schema):
        token = colander.SchemaNode(colander.String(),
                                    validator = context.validate_password_token,
                                    missing = u'',
                                    widget = deform.widget.HiddenWidget(),)
        password = colander.SchemaNode(colander.String(),
                                       validator=password_validation,
                                       widget=deform.widget.CheckedPasswordWidget(size=20),
                                       title=_('Password'))
                                       
    return _schema()
    

def PermissionSchema(context):
    """ Return selectable groups schema. This can be done in a smarter way with
        deferred schemas, but it can be like this for now.
    """
    
    root = find_root(context)
    user_choices = tuple(root['users'].keys())
    
    if context is root:
        #Only show administrator as selectable group in root
        group_choices = security.ROOT_ROLES
    else:
        #In other contexts (like Organisation) meeting roles apply
        group_choices = security.ORGANISATION_ROLES
        
    class UserIDAndGroupsSchema(colander.Schema):
        userid = colander.SchemaNode(
            colander.String(),
            validator=colander.OneOf(user_choices),
            widget = deform.widget.AutocompleteInputWidget(size=20,
                                                   values = user_choices,
                                                   min_length=1),
            )
        groups = colander.SchemaNode(
            deform.Set(allow_empty=True),
            title = _(u"Role"),
            widget=deform.widget.CheckboxChoiceWidget(values=group_choices,
                                                      missing=colander.null,)
            )

    class UserIDsAndGroupsSequenceSchema(colander.SequenceSchema):
        userid_and_groups = UserIDAndGroupsSchema(title=_(u'Roles for user'),)
        
    class Schema(colander.Schema):
        userids_and_groups = UserIDsAndGroupsSequenceSchema(title=_(u'Role settings for users'))
    
    return Schema()
