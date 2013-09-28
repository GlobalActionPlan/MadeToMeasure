import unittest
from datetime import datetime
from datetime import timedelta
import pytz

from pyramid import testing
from zope.interface.verify import verifyObject
from zope.component.interfaces import IFactory

from madetomeasure.interfaces import IDateTimeHelper


class DateTimeHelperTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.date_time_helper import DateTimeHelper
        return DateTimeHelper("Europe/Stockholm", 'en')

    def test_interface(self):
        obj = self._make_obj()
        self.failUnless(verifyObject(IDateTimeHelper, obj))

    def test_d_format(self):
        obj = self._make_obj()
        date = obj.timezone.localize(datetime.strptime('1999-12-13', "%Y-%m-%d"))
        self.assertEqual(obj.d_format(date), u'12/13/99')

    def test_t_format(self):
        obj = self._make_obj()
        date_and_time = obj.timezone.localize(datetime.strptime('1999-12-14 19:12', "%Y-%m-%d %H:%M"))
        self.assertEqual(obj.t_format(date_and_time), u'7:12 PM')

    def test_dt_format(self):
        obj = self._make_obj()
        date_and_time = obj.timezone.localize(datetime.strptime('1999-12-14 19:12', "%Y-%m-%d %H:%M"))
        self.assertEqual(obj.dt_format(date_and_time), '12/14/99, 7:12 PM')

    def test_datetime_localize(self):
        obj = self._make_obj()
        fmt = '%Y-%m-%d %H:%M %Z%z'
        date_time = datetime.strptime('1999-12-14 19:12', "%Y-%m-%d %H:%M")
        localized_dt = obj.timezone.localize(date_time)
        result = localized_dt.strftime(fmt)
        self.assertEquals(result, '1999-12-14 19:12 CET+0100')

    def test_tz_to_utc(self):
        obj = self._make_obj()
        fmt = '%Y-%m-%d %H:%M %Z%z'
        date_time = datetime.strptime('1999-12-14 19:12', "%Y-%m-%d %H:%M")
        localized_dt = obj.timezone.localize(date_time)
        utc_dt = obj.tz_to_utc(localized_dt)
        result = utc_dt.strftime(fmt)
        self.assertEquals(result, '1999-12-14 18:12 UTC+0000')

    def test_utc_to_tz(self):
        obj = self._make_obj()
        fmt = '%Y-%m-%d %H:%M %Z%z'
        date_time = datetime.strptime('1999-12-14 18:12', "%Y-%m-%d %H:%M")
        utc_dt = pytz.utc.localize(date_time, pytz.utc)
        local_dt = obj.utc_to_tz(utc_dt)
        result = local_dt.strftime(fmt)
        self.assertEquals(result, '1999-12-14 19:12 CET+0100')

    def test_utcnow(self):
        obj = self._make_obj()
        now = obj.utcnow()
        self.assertEquals(now.tzinfo, pytz.utc)

    def test_localnow(self):
        obj = self._make_obj()
        now = obj.localnow()
        # we don't check for exactly equal timezones due to DST changes
        self.assertEquals(str(now.tzinfo), str(obj.timezone))

    def test_dst_timedelta(self):
        """Check that timedeltas take DST into account.
        """
        obj = self._make_obj()
        date_time1 = datetime.strptime('1999-12-14 18:12', "%Y-%m-%d %H:%M")
        date_time2 = datetime.strptime('1999-08-14 18:12', "%Y-%m-%d %H:%M")
        l_dt1 = obj.timezone.localize(date_time1)
        l_dt2 = obj.timezone.localize(date_time2)

        self.assertNotEqual(l_dt1 - l_dt2, timedelta(days=122))
        self.assertEquals(l_dt1 - l_dt2, timedelta(days=122, hours=1))

    def test_registration(self):
        self.config.include('madetomeasure.models.date_time_helper')
        self.failUnless(self.config.registry.queryUtility(IFactory, 'dt_helper'))
