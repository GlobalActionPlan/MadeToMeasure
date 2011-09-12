from hashlib import sha1

from repoze.folder import Folder
from zope.interface import implements

from madetomeasure.interfaces import *
from madetomeasure import MadeToMeasureTSF as _


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = bootstrap_root()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']


def bootstrap_root():
    root = SiteRoot()
    root['users'] = Users()
    #Create admin user with password admin as standard
    admin = User()
    admin.set_password('admin')
    admin.set_title('Administrator')
    root['users']['admin'] = admin
    
    root['surveys'] = Surveys()
    root['participants'] = Participants()
    
    return root


def get_sha_password(password):
    """ Encode a plaintext password to sha1. """
    if isinstance(password, unicode):
        password = password.encode('UTF-8')
    return 'SHA1:' + sha1(password).hexdigest()


class SiteRoot(Folder):
    implements(ISiteRoot)
    content_type = 'SiteRoot'
    display_name = _(u"Site root")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name

class Users(Folder):
    """ Container for system users. These are translators, managers
        or any other folks that need to login.
    """
    implements(IUsers)
    content_type = 'Users'
    display_name = _(u"Users")
    allowed_contexts = () #Not manually addable
    
    def get_title(self):
        return self.display_name


class User(Folder):
    """ A system user """
    implements(IUser)
    content_type = 'User'
    display_name = _(u"User")
    allowed_contexts = ('Users')
    
    @property
    def userid(self):
        return self.__name__
    
    def set_title(self, value):
        self.__title__ = value
    
    def get_title(self):
        return getattr(self, '__title__', '')
    
    def set_email(self, value):
        self.__email__ = value
    
    def get_email(self):
        return getattr(self, '__email__', '')

    def set_password(self, value):
        self.__password__ = get_sha_password(value)
    
    def check_password(self, value):
        """ Check a plaintext password against stored encrypted password. """
        hash = get_sha_password(value)
        return hash == self.get_password()

    def get_password(self):
        return self.__password__
    

class Surveys(Folder):
    implements(ISurveys)
    content_type = 'Surveys'
    display_name = _(u"Surveys")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name

class Survey(Folder):
    implements(ISurvey)
    content_type = 'Survey'
    display_name = _(u"Survey")
    allowed_contexts = ('Surveys')


class Participants(Folder):
    """ Container for participant objects. """
    implements(IParticipants)
    content_type = 'Participants'
    display_name = _(u"Participants")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name
    

class Participant(Folder):
    """ A Participant is a light-weight user object. They're not meant to be able to login.
    """
    implements(IParticipant)
    content_type = 'Participant'
    display_name = _(u"Participants")
    allowed_contexts = ('Participants') #Not manually addable




    