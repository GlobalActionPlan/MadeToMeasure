from datetime import timedelta
from datetime import datetime
import pytz

from zope.interface import implements
from babel.dates import format_date
from babel.dates import format_time
from babel.dates import format_datetime

from madetomeasure.interfaces import IDateTimeHelper
from madetomeasure import MadeToMeasureTSF as _


class DateTimeHelper(object):
    """ Class to help with date conversion/display. """
    implements(IDateTimeHelper)
    
    def __init__(self, timezone, locale):
        self.timezone = pytz.timezone(timezone)
        self.locale = locale

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
    """ Register DateTimeHelper as a factory.
        Checkout factories in Zope Component Architechture docs.
        Example: registry.createObject('dt_helper', "GMT", "en")
    """
    from zope.component.factory import Factory
    from zope.component.interfaces import IFactory
    
    factory = Factory(DateTimeHelper, 'DateTimeHelper')
    config.registry.registerUtility(factory, IFactory, 'dt_helper')

