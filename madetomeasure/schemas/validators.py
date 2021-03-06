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

@colander.deferred
def deferred_login_validator(form, kw):
    context = kw['context']
    root = find_root(context)
    return LoginPasswordValidator(root)


class LoginPasswordValidator(object):
    """ Validate a password during login. context must be site root."""
    
    def __init__(self, context):
        self.context = context
        
    def __call__(self, form, value):
        exc = colander.Invalid(form, u"Login invalid") #Raised if trouble
        password = value['password']
        userid_or_email = value['userid_or_email']
        if '@' in userid_or_email:
            #assume email
            user = self.context['users'].get_user_by_email(userid_or_email)
        else:
            user = self.context['users'].get(userid_or_email)
        if not user:
            raise exc
        #Validate password
        pw_field = user.get_custom_field('password')
        if not pw_field.check_input(password):
            exc['password'] = _(u"Wrong password. Remember that passwords are case sensitive.")
            raise exc


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


@colander.deferred
def deferred_confirm_delete_with_title_validator(node, kw):
    context = kw['context']
    return ConfirmDeleteWithTitleValidator(context)


class ConfirmDeleteWithTitleValidator(object):

    def __init__(self, context, msg = None):
        self.context = context
        self.msg = msg and msg or _(u"Doesn't match")
    
    def __call__(self, node, value):
        if self.context.title != value:
            raise colander.Invalid(node, self.msg)
