import colander
import deform

from madetomeasure.schemas.questions import deferred_question_type_widget
from madetomeasure import MadeToMeasureTSF as _


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


class SurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    question_type = colander.SchemaNode(colander.String(),
                                        widget=deferred_question_type_widget,)


class SectionsSequenceSchema(colander.SequenceSchema):
    section = SurveySectionSchema()


class AddSurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    sections = SectionsSequenceSchema(title=_(u"Add sections"),)