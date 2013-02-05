from slugify import slugify
from pyramid.threadlocal import get_current_request
from pyramid.security import authenticated_userid
from pyramid.traversal import find_interface
from pyramid.traversal import find_root
from pyramid.i18n import get_locale_name
from pyramid.interfaces import ISettings
from zope.component import createObject

from madetomeasure.interfaces import ISurvey
from madetomeasure import MadeToMeasureTSF as _


def appmaker(zodb_root):
    try:
        return zodb_root['app_root']
    except KeyError:
        app_root = bootstrap_root()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
        return zodb_root['app_root']


def bootstrap_root():
    from madetomeasure.models.root import SiteRoot
    from madetomeasure.models.users import User
    from madetomeasure.models.users import Users
    from madetomeasure.models.surveys import Surveys
    from madetomeasure.models.participants import Participants
    from madetomeasure.models.questions import Questions
    from madetomeasure import security

    root = SiteRoot(creators=['admin'], title=_(u"Made To Measure"))
    root['users'] = Users(title = _(u"Users"))
    #Create admin user with password admin as standard
    admin = User(password='admin', first_name="M2M", last_name="Administrator")
    root['users']['admin'] = admin
    #Add admin to group managers
    root.add_groups('admin', [security.ROLE_ADMIN])
    root['participants'] = Participants(title=_(u"Participants"))
    root['questions'] = Questions(title=_(u"Questions"))
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
    else:
        user = root['users'].get(userid)
        tz = user.get_time_zone()

    locale = get_locale_name(request)
    #FIXME: Default lang settable on user profile too, or in request?
    return createObject('dt_helper', tz, locale)

def select_language(context, request=None):
    """ Try to pick a language for the current survey participant according to
        the Survey settings or the lang session variable.
    """
    survey = find_interface(context, ISurvey)
    if survey is None:
        raise ValueError("Can't find a Survey object in context traversal path. context was: %s" % context)
    
    langs = survey.get_available_languages()
    #Only one language?
    if len(langs) == 1:
        return tuple(langs)[0]
    
    if request is None:
        request = get_current_request()
    
    return request.cookies.get('_LOCALE_', None)


#def find_all_of_iface(context, iface):
#    """ Traverser that will find all objects from context and below
#        implementing a specific interface.
#    """
#    def _recurse(context, results):
#        for obj in context.values():
#            if iface.providedBy(obj):
#                results.add(obj)
#            _recurse(obj, results)
#    
#    results = set()
#    _recurse(context, results)
#    return results
