import colander
import deform
from pyramid.traversal import find_root

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.questions import deferred_question_type_widget
from madetomeasure.schemas.validators import multiple_email_validator


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

@colander.deferred
def deferred_questions_for_types_widget(node, kw):
    question_types = kw['question_types']
    context = kw['context']
    root = find_root(context)
    questions = root['questions']
    
    results = set()
    for question_type in question_types:
        results.update(questions.questions_by_type(question_type))
    
    choices = [(x.__name__, x.get_title()) for x in results]
    return deform.widget.CheckboxChoiceWidget(values=choices)


class SurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    from_address = colander.SchemaNode(colander.String(),
                                       validator=colander.Email(),)
    mail_message = colander.SchemaNode(colander.String(),
                                       widget=deform.widget.TextAreaWidget(rows=10, cols=50))
    finished_text = colander.SchemaNode(colander.String(),
                                        widget=deform.widget.TextAreaWidget(rows=10, cols=50),
                                        default=_(u"Thanks a lot for filling out the survey."),)

class AddSurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    question_type = colander.SchemaNode(colander.String(),
                                        widget=deferred_question_type_widget,)
    

class EditSurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    question_ids = colander.SchemaNode(deform.Set(),
                                       title = _(u"Questions in this survey section"),
                                       widget=deferred_questions_for_types_widget,)


class SurveyInvitationSchema(colander.Schema):
    invitation_emails = colander.SchemaNode(colander.String(),
                                            title = _(u"Participant email addresses - add one per row."),
                                            validator = multiple_email_validator,
                                            widget=deform.widget.TextAreaWidget(rows=10, cols=50),)
