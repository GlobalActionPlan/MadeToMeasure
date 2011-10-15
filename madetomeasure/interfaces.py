from zope.interface import Interface
from zope.interface import Attribute
from betahaus.pyracont.interfaces import IBaseFolder


class ISiteRoot(IBaseFolder):
    """ SiteRoot model. """


class IUsers(IBaseFolder):
    """ Users model. """


class IUser(IBaseFolder):
    """ User model. """


class ISurveys(IBaseFolder):
    """ Surveys model. """


class ISurvey(IBaseFolder):
    """ Survey model. """


class ISurveySection(IBaseFolder):
    """ Survey Section model. """


class IParticipants(IBaseFolder):
    """ Participants model. """


class IParticipant(IBaseFolder):
    """ Participant model. """


class IQuestions(IBaseFolder):
    """ A questions model - contains question objects. """


class IQuestion(IBaseFolder):
    """ A question model. """


class IOrganisation(IBaseFolder):
    """ An organisation model. """
    variants = Attribute("Question variants storage")
        
    def get_variant(question_uid, lang):
        """ Returns variant of question for language if there is one """
        
    def set_variant(question_uid, lang, value):
        """ Sets variants """


class IQuestionNode(Interface):
    """ A utility that will create a question colander.SchemaNode when called. """

    type_title = Attribute("Readable title for this class. Used in question choices for instance.")
    widget = Attribute("Which widget to use when running the 'node' method")
    default_kwargs = Attribute("Any kwargs passed along to init will be stored here."
                               "They will be passed along to the colander.SchemaNode constructed when node is run.")

    def __init__(type_title, widget, **kwargs):
        """ Create instance.
            widget must be a deform widget.
            kwargs will be passed along to the colander.SchemaNode when
            node method is run.
        """
    
    def node(name, **kwargs):
        """ Return a schema node.
            name argument is the nodes name in the schema
            kwargs here will override the node_kwargs attribute
        """
    
    def render_result(request, data):
        """ Render the result of this specific type of question.
            Returns a renderer.
            Data is the result data to be displayed. It must be of this questions own format.
        """


class IQuestionTranslations(Interface):
    """ Helper util when handling runtime translation of questions. """
    default_locale_name = Attribute("Default locale country code, like 'en'")
    available_languages = Attribute("A list of all available languages country codes")
    translatable_languages = Attribute("Same as available_languages, but minus default_locale_name value")
    
    def title_for_code(lang):
        """ Return readable name from a country code. """
    
    def add_translations_schema(schema):
        """ Fetch all possible translations (according to settings)
            and create a shecma with each lang as a node.
        """


class IDateTimeHelper(Interface):
    """ Helper util for datetime things. """


class ISecurityAware(Interface):
    """ Mixin for all content that should handle groups.
        Principal in this terminology is a userid or a group id.
    """
    
    def get_groups(principal):
        """ Return groups for a principal in this context.
            The special group "role:Owner" is never inherited.
        """

    def add_groups(principal, groups):
        """ Add a groups for a principal in this context.
        """
    
    def set_groups(principal, groups):
        """ Set groups for a principal in this context. (This clears any previous setting)
        """

    def update_userids_permissions(value):
        """ Set permissions from a list of dicts with the following layout:
            {'userid':<userid>,'groups':<set of groups that the user should have>}.
        """

    def get_security():
        """ Return the current security settings.
        """

    def list_all_groups():
        """ Returns a set of all groups in this context. """
