from datetime import datetime
from datetime import timedelta
from hashlib import sha1
from random import choice
import string

from pyramid.url import resource_url
from zope.interface import implements
from zope.component import getUtility
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.i18n import get_localizer
from pyramid.interfaces import ISettings

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

    def get_user_by_email(self, email):
        for user in self.values():
            if user.get_email() == email:
                return user


class User(BaseFolder):
    """ A system user """
    implements(IUser)
    content_type = 'User'
    display_name = _(u"User")
    allowed_contexts = ('Users',)
    
    @property
    def userid(self):
        return self.__name__
        
    def get_title(self):
        title = "%s %s" % (self.get_first_name(), self.get_last_name())
        return title.strip()

    def set_title(self, value):
        """ For compatibility, shouldn't be used"""
        pass

    def set_email(self, value):
        self.__email__ = value
    
    def get_email(self):
        return getattr(self, '__email__', '')

    def set_first_name(self, value):
        self.__first_name__ = value
    
    def get_first_name(self):
        return getattr(self, '__first_name__', '')

    def set_last_name(self, value):
        self.__last_name__ = value

    def get_last_name(self):
        return getattr(self, '__last_name__', '')

    def get_time_zone(self):
        tz = getattr(self, '__time_zone__', None)
        if tz is None:
            return getUtility(ISettings)['default_timezone']
        return tz

    def set_time_zone(self, value):
        self.__time_zone__ = value

    def set_password(self, value):
        self.__password__ = get_sha_password(value)
    
    def check_password(self, value):
        """ Check a plaintext password against stored encrypted password. """
        hash = get_sha_password(value)
        return hash == self.get_password()

    def get_password(self):
        return self.__password__
        
    def new_request_password_token(self, request):
        """ Set a new request password token and email user. """
        locale = get_localizer(request)
        
        self.__token__ = RequestPasswordToken()
        
        #FIXME: Email should use a proper template
        pw_link = "%stoken_pw?token=%s" % (resource_url(self, request), self.__token__())
        body = locale.translate(_('request_new_password_text',
                 default=u"password link: ${pw_link}",
                 mapping={'pw_link':pw_link},))
        
        msg = Message(subject=_(u"Password reset request from MadeToMeasure"),
                       recipients=[self.get_email()],
                       body=body)

        mailer = get_mailer(request)
        mailer.send(msg)
        
    def remove_password_token(self):
        self.__token__ = None

    def validate_password_token(self, node, value):
        """ Validate input from a colander form. See token_password_change schema """
        #FIXME: We need to handle an error here in a nicer way
        self.__token__.validate(value)


class RequestPasswordToken(object):

    def __init__(self):
        self.token = ''.join([choice(string.letters + string.digits) for x in range(30)])
        self.created = datetime.utcnow()
        self.expires = self.created + timedelta(days=3)
        
    def __call__(self):
        return self.token
    
    def validate(self, value):
        if value != self.token:
            raise ValueError("Token doesn't match.")
        if datetime.utcnow() > self.expires:
            raise ValueError("Token expired.")
    
