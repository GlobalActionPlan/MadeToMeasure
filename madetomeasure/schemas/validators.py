import colander

from pyramid.traversal import find_root

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IUser


def multiple_email_validator(node, value):
    """ Checks that each line of value is a correct email
    """
    validator = colander.Email()
    invalid = []
    for email in value.splitlines():
        email = email.strip()
        if not email:
            continue
        try:
            validator(node, email)
        except colander.Invalid:
            invalid.append(email)
    if invalid:
        emails = ", ".join(invalid)
        raise colander.Invalid(node, _(u"The following addresses is invalid: ${emails}", mapping={'emails': emails}))


@colander.deferred
def deferred_userid_or_email_validation(node, kw):
    """ Checks that a user object can be retrieved by an email address or a UserID. """
    context = kw['context']
    root = find_root(context)
    return UseridOrEmailValidator(root['users'])


class UseridOrEmailValidator(object):
    """ Make sure a userid or an email address can be used to fetch a user object.
    """
    def __init__(self, context):
        self.context = context

    def __call__(self, node, value):
        #userid here can be either an email address or a login name
        if '@' in value:
            #assume email
            user = self.context.get_user_by_email(value)
        else:
            user = self.context.get(value)
        if not IUser.providedBy(user):
            raise colander.Invalid(node, _(u"Login incorrect"))
