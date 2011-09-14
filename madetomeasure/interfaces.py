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


class ISurveySection(Interface):
    """ Survey Section model. """


class IParticipants(Interface):
    """ Participants model. """


class IParticipant(Interface):
    """ Participant model. """


class IQuestions(Interface):
    """ A questions model - contains question objects. """


class IQuestion(Interface):
    """ A question model. """


class IQuestionNode(Interface):
    """ A utility that will create a question colander.SchemaNode when called. """

    def __init__(type_title, widget):
        """ Create instance.
            widget must be  """
    
    def node(name, **kw): 
        """ Return a schema node.
            name argument is the nodes name in the schema
            You can pass along keyword arguments that will be accepted
            by the SchemaNode class.
            Tip: We use title and validator
        """
    
    def render_result(request, data):
        """ Render the result of this specific type of question.
            Returns a renderer.
            Data is the result data to be displayed. It must be of this questions own format.
        """
        