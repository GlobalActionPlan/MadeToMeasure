from pytz import common_timezones
from operator import itemgetter

import colander
import deform
from zope.component import getUtility


from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.questions import deferred_question_type_widget
from madetomeasure.schemas.validators import multiple_email_validator
from madetomeasure.interfaces import IOrganisation
from madetomeasure.models.fields import TZDateTime
from madetomeasure.schemas.common import time_zone_node
from madetomeasure.interfaces import IOrganisation, IQuestionTranslations


@colander.deferred
def deferred_available_languages_widget(node, kw):
    util = getUtility(IQuestionTranslations)
    sort = []
    for lang in util.available_languages:
        sort.append((lang, util.title_for_code_default(lang).lower()))
    sort = sorted(sort, key=itemgetter(1))
    choices = []
    for (lang, name) in sort:
        name = "%s - %s (%s)" % (util.title_for_code_default(lang), util.title_for_code(lang), lang)
        choices.append((lang, name))
    return deform.widget.CheckboxChoiceWidget(values=choices)


def heading_translations_node():
    return colander.Schema(title=_("Section heading translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema



class SurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    start_time = colander.SchemaNode(
         TZDateTime(),
         title = _(u"Start time for survey"),
         missing=colander.null,
         widget=deform.widget.DateTimeInputWidget(options={'timeFormat': 'hh:mm'},),
    )

    end_time = colander.SchemaNode(
         TZDateTime(),
         title = _(u"End time for survey"),
         missing=colander.null,
         widget=deform.widget.DateTimeInputWidget(options={'timeFormat': 'hh:mm'}),
    )
    from_address = colander.SchemaNode(colander.String(),
                                       validator=colander.Email(),)
    finished_text = colander.SchemaNode(colander.String(),
                                        widget=deform.widget.RichTextWidget(),
                                        default=_(u"Thanks a lot for filling out the survey."),)
    time_zone = time_zone_node()
    available_languages = colander.SchemaNode(deform.Set(),
                                              widget=deferred_available_languages_widget,
                                              title=_("Available languages"),)


class SurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    heading_translations = heading_translations_node()
    structured_question_ids = colander.Schema(title=_(u"Select participating questions"),)


class SurveyInvitationSchema(colander.Schema):
    message = colander.SchemaNode(colander.String(),
                                  widget=deform.widget.RichTextWidget(),
                                  default=_('Please fill in the survey'),)
    emails = colander.SchemaNode(colander.String(),
                                 title = _(u"Participant email addresses - add one per row."),
                                 validator = multiple_email_validator,
                                 widget=deform.widget.TextAreaWidget(rows=10, cols=50),)


class SurveyReminderSchema(colander.Schema):
    message = colander.SchemaNode(colander.String(),
                                  title = _(u"Reminder message"),
                                  widget=deform.widget.RichTextWidget(),)


@colander.deferred
def deferred_select_language_widget(node, kw):
    langs = kw['languages']
    util = getUtility(IQuestionTranslations)
    sort = []
    for lang in langs:
        sort.append((lang, util.title_for_code_default(lang).lower()))
    sort = sorted(sort, key=itemgetter(1))
    choices = []
    for (lang, name) in sort:
        name = "%s - %s (%s)" % (util.title_for_code_default(lang), util.title_for_code(lang), lang)
        choices.append((lang, name))
    return deform.widget.CheckboxChoiceWidget(values=choices)


class SurveyLangugageSchema(colander.Schema):
    selected_language = colander.SchemaNode(colander.String(),
                                          title=_("Choose language"),
                                          widget=deferred_select_language_widget,)
