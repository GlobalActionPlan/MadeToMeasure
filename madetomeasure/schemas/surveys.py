from pytz import common_timezones
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
    choices = []
    for lang in util.available_languages:
        choices.append((lang, util.lang_names[lang]))
    return deform.widget.CheckboxChoiceWidget(values=choices)


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
    mail_message = colander.SchemaNode(colander.String(),
                                       widget=deform.widget.TextAreaWidget(rows=10, cols=50))
    finished_text = colander.SchemaNode(colander.String(),
                                        widget=deform.widget.TextAreaWidget(rows=10, cols=50),
                                        default=_(u"Thanks a lot for filling out the survey."),)
    time_zone = time_zone_node()
    available_languages = colander.SchemaNode(deform.Set(),
                                              widget=deferred_available_languages_widget,
                                              title=_("Available languages"),)


class SurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    structured_question_ids = colander.Schema(title=_(u"Select participating questions"),)


class SurveyInvitationSchema(colander.Schema):
    invitation_emails = colander.SchemaNode(colander.String(),
                                            title = _(u"Participant email addresses - add one per row."),
                                            validator = multiple_email_validator,
                                            widget=deform.widget.TextAreaWidget(rows=10, cols=50),)


class SurveyReminderSchema(colander.Schema):
    message = colander.SchemaNode(colander.String(),
                                  title = _(u"Remainder message"),
                                  widget=deform.widget.TextAreaWidget(rows=10, cols=50),)


@colander.deferred
def deferred_select_language_widget(node, kw):
    langs = kw['languages']
    util = getUtility(IQuestionTranslations)
    choices = []
    for lang in langs:
        choices.append((lang, util.lang_names[lang]))
    return deform.widget.RadioChoiceWidget(values=choices)

class SurveyLangugageSchema(colander.Schema):
    selected_language = colander.SchemaNode(colander.String(),
                                          title=_("Chose language"),
                                          widget=deferred_select_language_widget,)
