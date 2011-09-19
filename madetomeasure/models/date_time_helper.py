from datetime import timedelta
from datetime import datetime
import pytz

from zope.interface import implements
from pyramid.i18n import get_locale_name
from pyramid.threadlocal import get_current_request
from babel.dates import format_date
from babel.dates import format_time
from babel.dates import format_datetime

from madetomeasure.interfaces import IDateTimeHelper
from madetomeasure import MadeToMeasureTSF as _


class DateTimeHelper(object):
    """ Adapter for requests to help with date conversion/display. """
    implements(IDateTimeHelper)
    
    def __init__(self, request):
        timezone = request.session.get('timezone', None)
        if not timezone:
            timezone = request.registry.settings['default_timezone']
        
        self.timezone = pytz.timezone(timezone)
        self.locale = get_locale_name(request)

    def utcnow(self):
        return utcnow()

    def localnow(self):
        """ Get the current datetime localized to the specified timezone.
        """
        utcnow = self.utcnow()
        return self.utc_to_tz(utcnow)

    def tz_to_utc(self, datetime_tz):
        """Convert the provided datetime object from local to UTC.

        The datetime_tz object is expected to have the timezone specified in
        the timezone attribute.
        """
        return datetime_tz.astimezone(pytz.utc)

    def utc_to_tz(self, datetime_tz):
        """ Convert the provided datetime object from UTC to local.

            Timezone must be a pytz timezone object or a string.
            In case timezone is a string, pytz will raise UnknownTimeZoneError
            if the timezone doesn't exist.
        """
        return self.timezone.normalize(datetime_tz.astimezone(self.timezone))

    def d_format(self, value, format='short'):
        """ Format the given date in the given format.
            Will also convert to current timezone from utc.
        """
        localtime = self.utc_to_tz(value)
        return format_date(localtime, format=format, locale=self.locale)

    def t_format(self, value, format='short'):
        localtime = self.utc_to_tz(value)
        return format_time(localtime, format=format, locale=self.locale)
    
    def dt_format(self, value, format='short'):
        """ Format the given datetime in the given format.
            Will also convert to current timezone from utc.
        """
        localtime = self.utc_to_tz(value)
        return format_datetime(localtime, format=format, locale=self.locale)


def utcnow():
    """Get the current datetime localized to UTC.

    The difference between this method and datetime.utcnow() is
    that datetime.utcnow() returns the current UTC time but as a naive
    datetime object, whereas this one includes the UTC tz info."""

    naive_utcnow = datetime.utcnow()
    return pytz.utc.localize(naive_utcnow)


def includeme(config):
    """ Register DateTimeHelper as an adapter. """
    from pyramid.interfaces import IRequest
    config.registry.registerAdapter(DateTimeHelper, (IRequest,), IDateTimeHelper)

