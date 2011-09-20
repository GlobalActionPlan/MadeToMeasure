import colander
import deform
from pytz import common_timezones

from madetomeasure import MadeToMeasureTSF as _


def time_zone_node():
    return colander.SchemaNode(
        colander.String(),
        title = _(u"Timezone"),
        description = _(u"Try start typing a timezone"),
        validator = colander.OneOf(common_timezones),
        widget = deform.widget.AutocompleteInputWidget(size=60,
                                                   values = common_timezones,
                                                   min_length=1),
    )
