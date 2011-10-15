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
from pyramid.security import Allow, Everyone
from pyramid.threadlocal import get_current_request
from pyramid.security import authenticated_userid
from betahaus.pyracont import BaseFolder

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IUser
from madetomeasure.interfaces import IUsers
from madetomeasure.models.security_aware import SecurityAware


class Users(BaseFolder, SecurityAware):
    """ Container for system users. These are translators, managers
        or any other folks that need to login.
    """
    implements(IUsers)
    content_type = 'Users'
    display_name = _(u"Users")
    allowed_contexts = () #Not manually addable

    def get_user_by_email(self, email):
        for user in self.values():
            if user.get_field_value('email') == email:
                return user


class User(BaseFolder, SecurityAware):
    """ A system user """
    implements(IUser)
    content_type = 'User'
    display_name = _(u"User")
    allowed_contexts = ('Users',)
    custom_fields = {'password': 'PasswordField'}
    custom_accessors = {'title': 'get_title',
                        'time_zone': 'get_time_zone'}
    custom_mutators = {'title': 'set_title'}
    
    @property
    def __acl__(self):
        from madetomeasure import security
        request = get_current_request()
        userid = authenticated_userid(request)
        if userid == self.userid:
            return [(Allow, Everyone, (security.VIEW, security.EDIT,)),]
        raise AttributeError("Go fetch parents acl")
    
    @property
    def userid(self):
        return self.__name__
        
    def get_title(self, **kw):
        """ Return a combo of firstname and lastname or the userid.
            default kw isn't used here.
        """
        title = "%s %s" % (self.get_field_value('first_name', u''), self.get_field_value('last_name', u''))
        title = title.strip()
        return title and title or self.userid

    def set_title(self, value, key=None):
        """ For compatibility, shouldn't be used"""
        pass

    def get_time_zone(self, default=None, **kwargs):
        """ custom accessor that uses default_timezone from settings as standard value, unless overridden. """
        marker = object()
        #To avoid loop...
        tz = self._field_storage.get('time_zone', marker)
        if tz is marker:
            return getUtility(ISettings)['default_timezone']
        return tz
    
    def check_password(self, value):
        """ Check a plaintext password against stored encrypted password. """
        field = self.get_custom_field('password')
        return field.check_input(value)

    def new_request_password_token(self, request):
        """ Set a new request password token and email user. """
        locale = get_localizer(request)
        
        self.__token__ = RequestPasswordToken()
        
        #FIXME: Email should use a proper template
        pw_link = "%stoken_pw?token=%s" % (resource_url(self, request), self.__token__())
        body = locale.translate(_('request_new_password_text',
                 default=u"password link: ${pw_link}",
                 mapping={'pw_link':pw_link},))
        
        #FIXME: What if email is empty...?
        msg = Message(subject=_(u"Password reset request from MadeToMeasure"),
                       recipients=[self.get_field_value('email')()],
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
    
