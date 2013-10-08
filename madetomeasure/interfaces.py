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


class ILocalQuestions(IBaseFolder):
    """ A questions model - contains question objects. """


class IQuestion(IBaseFolder):
    """ A question model. """
    tags = Attribute("A frozenset of used tags")
    is_variant = Attribute("Bool - Does this question have a variant?")
    is_local = Attribute("Bool - is this a local question?")
    is_required = Attribute("Bool - is this required?")


class IQuestionTypes(IBaseFolder):
    """ Container and handler for question types. """


class IQuestionType(IBaseFolder):
    """ Question type object. Contains information on a specific question type. Like "True or False"
        or a "Free text question".
    """
    allowed_contexts = Attribute("Contexts where this is allowed.")
    default_kwargs = Attribute("Default kwargs to pass along when constructing a question schema node.")
    uid_name = Attribute("Boolean - if true use UID as __name__ rather than trying to generate one from the title.")
    go_to_after_add = Attribute("String - Where to go after add. Usually something like 'edit'.")
    widget = Attribute("The currently set widget adapter or Nones")

    def node(name, lang = None, **kwargs):
        """ Return a colander.SchemaNode with the name specified. kwargs will be used when the SchemaNode
            is instantiated.
        """

    def count_occurences(data):
        """ Count occurences. Specific for each question type. """

    def render_result(request, data):
        """ Render result template. """

    def csv_header():
        """ CSV header when exporting. Called when an export is being performed."""

    def csv_export(data):
        """ Export this section as CSV. Called when an export is being performed."""

    def check_safe_delete(request):
        """ Investigate if it's safe to delete this question. Returns True/False + will append
            to request flash message if it isn't safe.
        """


class IChoiceQuestionType(IQuestionType):
    """ Single choice question type - stores strings.
    """


class IMultiChoiceQuestionType(IQuestionType):
    """ Multi choice question type - stores iterables with strings.
    """


class ITextQuestionType(IQuestionType):
    """ All the different text based questions must implement this interface.
    """


class IIntegerQuestionType(IQuestionType):
    """ Similar to text question, but stores an integer value.
    
        WILL BE REMOVED
    """


class INumberQuestionType(IQuestionType):
    """ Similar to text question, but stores a decimal value.
    """


class IChoice(IBaseFolder):
    """ Base object that makes the choices of a IQuestionType.
    
        I.e. the question type of radio buttons have different choices that can be made. Each one of those choices is an IChoice.
            
        Do you garbage recycle? (IQuestionType)
            * Yes (IChoice)
            * Sometimes (IChoice)
            * No (IChoice)    
    """

    def get_title(lang=None):
        """ Finds and returns the title based on 'lang'. 
            If no language is specified or no translation in specified language
            the system default title is returned instead.

            lang:
                Translation that should be used
        """

    def set_title_translations(value, **kw):
        """ Set translations for this ChoiceQuestionType.

            value:
                A dict or list of tuples with all the lang, translation pairs.
            **kw:
                Ignored, but is needed for compatibility with the rest of the system.
        """


class IOrganisation(IBaseFolder):
    """ An organisation model. """
    variants = Attribute("Question variants storage")
    questions = Attribute("Easy way to get a dict of all valid questions - local variants override global if there's a collision.")

    def get_variant(question_name, lang):
        """ Returns variant of question for language if there is one """

    def set_variant(question_name, lang, value):
        """ Sets variants """


class IQuestionNode(Interface):
    """ A utility that will create a question colander.SchemaNode when called. """

    title = Attribute("Readable title for this class. Used in question choices for instance.")
    widget = Attribute("Which widget to use when running the 'node' method")
    default_kwargs = Attribute("Any kwargs passed along to init will be stored here."
                               "They will be passed along to the colander.SchemaNode constructed when node is run.")

    def __init__(widget, **kwargs):
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


class IQuestionWidget(Interface):
    """ Selectable question widgets. """


class IQuestionTranslations(Interface):
    """ Helper util when handling runtime translation of questions. """
    default_locale_name = Attribute("Default locale country code, like 'en'")
    available_languages = Attribute("A list of all available languages country codes")
    translatable_languages = Attribute("Same as available_languages, but minus default_locale_name value")
    
    def title_for_code(lang):
        """ Return readable name from a country code. """
    
    def add_translations_schema(schema, context, richtext=False):
        """ Fetch all possible translations (according to settings)
            and create a shecma with each lang as a node.
            If richtext is true, a richtextfield will be used instead.
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
