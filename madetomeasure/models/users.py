from hashlib import sha1

from zope.interface import implements

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *
from madetomeasure.models.base import BaseFolder


def get_sha_password(password):
    """ Encode a plaintext password to sha1. """
    if isinstance(password, unicode):
        password = password.encode('UTF-8')
    return 'SHA1:' + sha1(password).hexdigest()


class Users(BaseFolder):
    """ Container for system users. These are translators, managers
        or any other folks that need to login.
    """
    implements(IUsers)
    content_type = 'Users'
    display_name = _(u"Users")
    allowed_contexts = () #Not manually addable
    
    def get_title(self):
        return self.display_name

    def set_title(self, value):
        pass


class User(BaseFolder):
    """ A system user """
    implements(IUser)
    content_type = 'User'
    display_name = _(u"User")
    allowed_contexts = ('Users',)
    
    @property
    def userid(self):
        return self.__name__
    
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
    