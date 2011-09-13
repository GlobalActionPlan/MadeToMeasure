from madetomeasure.schemas.questions import AddQuestionSchema
from madetomeasure.schemas.questions import EditQuestionSchema
from madetomeasure.schemas.surveys import AddSurveySchema
from madetomeasure.schemas.surveys import AddSurveySectionSchema
from madetomeasure.schemas.surveys import SurveyInvitationSchema
from madetomeasure.schemas.surveys import EditSurveySectionSchema

from madetomeasure.schemas.question_types import FreeTextQuestionSchema
from madetomeasure.schemas.question_types import ImportanceScaleQuestionSchema
from madetomeasure.schemas.question_types import FrequencyScaleQuestionSchema

from madetomeasure.schemas.system import LoginSchema


CONTENT_SCHEMAS = {'AddQuestion':AddQuestionSchema,
                   'EditQuestion':EditQuestionSchema,
                   'AddSurvey':AddSurveySchema,
                   'AddSurveySection':AddSurveySectionSchema,
                   'EditSurveySection':EditSurveySectionSchema,
                   'SurveyInvitation':SurveyInvitationSchema,}


QUESTION_SCHEMAS = {'FreeTextQuestion': FreeTextQuestionSchema,
                    'ImportanceScaleQuestion': ImportanceScaleQuestionSchema,
                    'FrequencyScaleQuestion': FrequencyScaleQuestionSchema,}