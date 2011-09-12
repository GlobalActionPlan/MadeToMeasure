import colander
import deform

from madetomeasure import MadeToMeasureTSF as _


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