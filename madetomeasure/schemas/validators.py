import colander

from madetomeasure import MadeToMeasureTSF as _


def multiple_email_validator(node, value):
    """ Checks that each line of value is a correct email
    """

    validator = colander.Email()
    invalid = []
    for email in value.splitlines():
        try:
            validator(node, email)
        except colander.Invalid:
            invalid.append(email)
            
    if invalid:
        emails = ", ".join(invalid)
        raise colander.Invalid(node, _(u"The following addresses is invalid: ${emails}", mapping={'emails': emails}))
