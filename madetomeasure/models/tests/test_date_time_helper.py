import unittest
from datetime import datetime
from datetime import timedelta
import pytz

from pyramid import testing
from zope.interface.verify import verifyObject
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from madetomeasure.interfaces import IDateTimeHelper


class DateTimeHelperTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self, request):
        from madetomeasure.models.date_time_helper import DateTimeHelper
        if 'default_timezone' not in request.registry.settings:
            request.registry.settings['default_timezone'] = "Europe/Stockholm"
        return DateTimeHelper(request)

    def test_interface(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        self.failUnless(verifyObject(IDateTimeHelper, obj))

    def test_session_tz_negotiation(self):
        sessionfact = UnencryptedCookieSessionFactoryConfig('testing')
        self.config.set_session_factory(sessionfact)
        request = testing.DummyRequest()
        request.session['timezone'] = 'GMT'
        
        obj = self._make_obj(request)
        self.assertEqual(obj.timezone.zone, 'GMT')


    def test_d_format(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        date = obj.timezone.localize(datetime.strptime('1999-12-13', "%Y-%m-%d"))
        self.assertEqual(obj.d_format(date), u'12/13/99')

    def test_t_format(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        date_and_time = obj.timezone.localize(datetime.strptime('1999-12-14 19:12', "%Y-%m-%d %H:%M"))
        self.assertEqual(obj.t_format(date_and_time), u'7:12 PM')

    def test_dt_format(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        date_and_time = obj.timezone.localize(datetime.strptime('1999-12-14 19:12', "%Y-%m-%d %H:%M"))
        self.assertEqual(obj.dt_format(date_and_time), '12/14/99 7:12 PM')

    def test_datetime_localize(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        fmt = '%Y-%m-%d %H:%M %Z%z'
        date_time = datetime.strptime('1999-12-14 19:12', "%Y-%m-%d %H:%M")
        localized_dt = obj.timezone.localize(date_time)
        result = localized_dt.strftime(fmt)
        self.assertEquals(result, '1999-12-14 19:12 CET+0100')

    def test_tz_to_utc(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        fmt = '%Y-%m-%d %H:%M %Z%z'
        date_time = datetime.strptime('1999-12-14 19:12', "%Y-%m-%d %H:%M")
        localized_dt = obj.timezone.localize(date_time)
        utc_dt = obj.tz_to_utc(localized_dt)
        result = utc_dt.strftime(fmt)
        self.assertEquals(result, '1999-12-14 18:12 UTC+0000')

    def test_utc_to_tz(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        fmt = '%Y-%m-%d %H:%M %Z%z'
        date_time = datetime.strptime('1999-12-14 18:12', "%Y-%m-%d %H:%M")
        utc_dt = pytz.utc.localize(date_time, pytz.utc)
        local_dt = obj.utc_to_tz(utc_dt)
        result = local_dt.strftime(fmt)
        self.assertEquals(result, '1999-12-14 19:12 CET+0100')

    def test_utcnow(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        now = obj.utcnow()
        self.assertEquals(now.tzinfo, pytz.utc)

    def test_localnow(self):
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        now = obj.localnow()
        # we don't check for exactly equal timezones due to DST changes
        self.assertEquals(str(now.tzinfo), str(obj.timezone))

    def test_dst_timedelta(self):
        """Check that timedeltas take DST into account.
        """
        request = testing.DummyRequest()
        obj = self._make_obj(request)
        date_time1 = datetime.strptime('1999-12-14 18:12', "%Y-%m-%d %H:%M")
        date_time2 = datetime.strptime('1999-08-14 18:12', "%Y-%m-%d %H:%M")
        l_dt1 = obj.timezone.localize(date_time1)
        l_dt2 = obj.timezone.localize(date_time2)

        self.assertNotEqual(l_dt1 - l_dt2, timedelta(days=122))
        self.assertEquals(l_dt1 - l_dt2, timedelta(days=122, hours=1))

    def test_registration(self):
        self.config.include('madetomeasure.models.date_time_helper')
        request = testing.DummyRequest()
        request.registry.settings['default_timezone'] = "GMT"
        self.failUnless(self.config.registry.queryAdapter(request, IDateTimeHelper))
