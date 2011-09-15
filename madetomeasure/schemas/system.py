import colander
import deform

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.users import password_validation


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
