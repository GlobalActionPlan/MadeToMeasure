from slugify import slugify
from pyramid.threadlocal import get_current_request
from pyramid.security import authenticated_userid
from pyramid.traversal import find_root
from pyramid.i18n import get_locale_name
from pyramid.interfaces import ISettings
from zope.component import createObject


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
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

    root = SiteRoot()
    root['users'] = Users()
    #Create admin user with password admin as standard
    admin = User()
    admin.set_password('admin')
    admin.set_title('Administrator')
    root['users']['admin'] = admin
    #Add admin to group managers
    root.add_groups('admin', [security.ROLE_ADMIN])
    
    root['participants'] = Participants()
    root['questions'] = Questions()
    
    
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
        tz = request.getUtility(ISettings)['default_timezone']
    else:
        user = root['users'].get(userid)
        tz = user.get_time_zone()

    locale = get_locale_name(request)
    #FIXME: Default lang settable on user profile too, or in request?
    return createObject('dt_helper', tz, locale)
#
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
