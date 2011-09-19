import colander
import deform
from pyramid.traversal import find_root, find_interface

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.questions import deferred_question_type_widget
from madetomeasure.schemas.validators import multiple_email_validator
from madetomeasure.interfaces import IOrganisation


@colander.deferred
def deferred_survey_title(node, kw):
    title = kw.get('survey_title', None)
    if title is None:
        raise ValueError("survey_title must be part of schema binding.")
    return title


@colander.deferred
def deferred_survey_section_title(node, kw):
    title = kw.get('survey_section_title', None)
    if title is None:
        raise ValueError("survey_section_title must be part of schema binding.")
    return title


class SurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    from_address = colander.SchemaNode(colander.String(),
                                       validator=colander.Email(),)
    mail_message = colander.SchemaNode(colander.String(),
                                       widget=deform.widget.TextAreaWidget(rows=10, cols=50))
    finished_text = colander.SchemaNode(colander.String(),
                                        widget=deform.widget.TextAreaWidget(rows=10, cols=50),
                                        default=_(u"Thanks a lot for filling out the survey."),)


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
