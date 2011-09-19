import datetime
import iso8601

from pyramid.threadlocal import get_current_request
from colander import DateTime, Invalid, null, _

from madetomeasure.interfaces import IDateTimeHelper


class TZDateTime(DateTime):
    """ A type representing a timezone-aware datetime object.

    It respects the timezone specified on creation. The datetime coming from
    the form is expected to be specified according to the local time zone, and
    is converted to UTC during deserialization. Serialization converts it back
    to the local timezone, so the conversion process is transparent to the user.
    """
    def _get_dt_helper(self):
        request = get_current_request()
        return request.registry.getAdapter(request, IDateTimeHelper)

    def serialize(self, node, appstruct):
        if appstruct is null:
            return null

        if type(appstruct) is datetime.date: # cant use isinstance; dt subs date
            appstruct = datetime.datetime.combine(appstruct, datetime.time())

        if not isinstance(appstruct, datetime.datetime):
            raise Invalid(node,
                          _("'${val}' is not valid as date and time",
                            mapping={'val':appstruct})
                          )
        dt = self._get_dt_helper()

        return dt.utc_to_tz(appstruct).strftime('%Y-%m-%d %H:%M')


    def deserialize(self, node, cstruct):
        if not cstruct:
            return null

        dt = self._get_dt_helper()

        try:
            result = datetime.datetime.strptime(cstruct, "%Y-%m-%dT%H:%M")

            # python's datetime doesn't deal correctly with DST, so we have
            # to use the pytz localize function instead
            result = result.replace(tzinfo=None)
            result = dt.timezone.localize(result)

        except (iso8601.ParseError, TypeError), e:
            try:
                year, month, day = map(int, cstruct.split('-', 2))
                result = datetime.datetime(year, month, day,
                                           tzinfo=self.default_tzinfo)
            except Exception, e:
                raise Invalid(node, _(self.err_template,
                                      mapping={'val':cstruct, 'err':e}))

        return dt.tz_to_utc(result)
