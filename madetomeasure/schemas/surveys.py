from pytz import common_timezones
import colander
import deform
from pyramid.traversal import find_root, find_interface

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.questions import deferred_question_type_widget
from madetomeasure.schemas.validators import multiple_email_validator
from madetomeasure.interfaces import IOrganisation
from madetomeasure.models.fields import TZDateTime
from madetomeasure.schemas.common import time_zone_node


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
