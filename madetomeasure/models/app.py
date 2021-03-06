from slugify import slugify
from pyramid.threadlocal import get_current_request
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
from pyramid.i18n import get_locale_name
from pyramid.interfaces import ISettings
from zope.component import createObject

from madetomeasure import MadeToMeasureTSF as _


def appmaker(zodb_root):
    try:
        return zodb_root['app_root']
    except KeyError:
        from repoze.evolution import ZODBEvolutionManager
        from madetomeasure.evolve import VERSION
        root = bootstrap_root()
        zodb_root['app_root'] = root
        import transaction
        transaction.commit()
        manager = ZODBEvolutionManager(root, evolve_packagename = 'madetomeasure.evolve', sw_version = VERSION)
        manager.set_db_version(VERSION)
        manager.transaction.commit()
        return root

def bootstrap_root():
    from madetomeasure.models.root import SiteRoot
    from madetomeasure.models.users import User
    from madetomeasure.models.users import Users
    from madetomeasure.models.participants import Participants
    from madetomeasure.models.questions import Questions
    from madetomeasure.models.question_types import QuestionTypes
    from madetomeasure.models.question_types import TextQuestionType
    from madetomeasure import security

    root = SiteRoot(creators=['admin'], title = u"Made To Measure")
    root['users'] = Users(title = _(u"Users"))
    #Create admin user with password admin as standard
    admin = User(password='admin', first_name="M2M", last_name="Administrator")
    root['users']['admin'] = admin
    #Add admin to group managers
    root.add_groups('admin', [security.ROLE_ADMIN])
    root['participants'] = Participants(title=_(u"Participants"))
    root['questions'] = Questions(title=_(u"Questions"))
    root['question_types'] = QuestionTypes()
    #Note, free_text_question is also used in tests!
    root['question_types']['free_text_question'] = TextQuestionType(title = u"Free text question",
                                                                    description = u"Just a text field",
                                                                    input_widget = 'text_widget')
    return root

def generate_slug(context, text, limit=20):
    """ Suggest a name for content that will be added.
        text is a title or similar to be used.
    """
    suggestion = slugify(text[:limit])
    
    #Is the suggested ID already unique?
    if suggestion not in context:
        return suggestion
    
    #ID isn't unique, let's try to generate a unique one.
    RETRY = 100
    i = 1
    while i <= RETRY:
        new_s = "%s-%s" % (suggestion, str(i))
        if new_s not in context:
            return new_s
        i += 1
    #If no id was found, don't just continue
    raise KeyError("No unique id could be found")

def get_users_dt_helper(request=None):
    """ Get authenticated users timezone, lang and return DateTimeHelper for it. """
    if request is None:
        request = get_current_request()
    userid = authenticated_userid(request)
    root = find_root(request.context)
    if root is None:
        tz = request.registry.getUtility(ISettings)['default_timezone']
        locale = get_locale_name(request)
    else:
        user = root['users'][userid]
        tz = user.get_time_zone()
        datetime_localisation = user.get_field_value('datetime_localisation', None)
        locale = datetime_localisation and datetime_localisation or get_locale_name(request)
    return createObject('dt_helper', tz, locale)
