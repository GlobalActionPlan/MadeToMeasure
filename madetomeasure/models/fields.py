import datetime
import iso8601

import colander
from colander import _ as CMF


from madetomeasure.models.app import get_users_dt_helper


class TZDateTime(colander.SchemaType):
    """ A type representing a timezone-aware datetime object.

    It respects the timezone specified on creation. The datetime coming from
    the form is expected to be specified according to the local time zone, and
    is converted to UTC during deserialization. Serialization converts it back
    to the local timezone, so the conversion process is transparent to the user.
    """
    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        if type(appstruct) is datetime.date: # cant use isinstance; dt subs date
            appstruct = datetime.datetime.combine(appstruct, datetime.time())

        if not isinstance(appstruct, datetime.datetime):
            raise colander.Invalid(node,
                                   CMF("'${val}' is not valid as date and time",
                                       mapping={'val':appstruct})
                                   )
        dt = get_users_dt_helper()

        return dt.utc_to_tz(appstruct).strftime('%Y-%m-%d %H:%M')

    def deserialize(self, node, cstruct):
        if not cstruct:
            return colander.null
        dt = get_users_dt_helper()
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
                raise colander.Invalid(node, CMF(self.err_template,
                                                 mapping={'val':cstruct, 'err':e}))
        return dt.tz_to_utc(result)
