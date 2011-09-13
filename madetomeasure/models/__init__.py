from madetomeasure.models.users import User
from madetomeasure.models.surveys import Survey
from madetomeasure.models.surveys import SurveySection
from madetomeasure.models.participants import Participant
from madetomeasure.models.questions import Question


CONTENT_TYPES = {'User':User,
                 'Survey':Survey,
                 'SurveySection':SurveySection,
                 'Participant':Participant,
                 'Question':Question,
                 }
