from zope.interface import Interface


class ISiteRoot(Interface):
    """ SiteRoot model. """


class IUsers(Interface):
    """ Users model. """


class IUser(Interface):
    """ User model. """


class ISurveys(Interface):
    """ Surveys model. """


class ISurvey(Interface):
    """ Survey model. """


class IParticipants(Interface):
    """ Participants model. """


class IParticipant(Interface):
    """ Participant model. """


class IQuestions(Interface):
    """ A questions model - contains question objects. """


class IQuestion(Interface):
    """ A question model. """