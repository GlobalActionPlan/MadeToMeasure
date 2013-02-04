from operator import itemgetter

import colander
import deform
from pytz import common_timezones
from zope.component import getUtility

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionTranslations


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

def _get_langs(omit = ()):
    util = getUtility(IQuestionTranslations)
    sort = []
    for lang in util.available_languages:
        if lang not in omit:
            sort.append((lang, util.title_for_code_default(lang).lower()))
    sort = sorted(sort, key=itemgetter(1))
    choices = []
    for (lang, name) in sort:
        name = "%s - %s (%s)" % (util.title_for_code_default(lang), util.title_for_code(lang), lang)
        choices.append((lang, name))
    return choices


@colander.deferred
def deferred_available_languages_widget(node, kw):
    return deform.widget.CheckboxChoiceWidget(values = _get_langs())


@colander.deferred
def deferred_translator_languages_widget(node, kw):
    return deform.widget.CheckboxChoiceWidget(values = _get_langs(omit = ('en',)))
