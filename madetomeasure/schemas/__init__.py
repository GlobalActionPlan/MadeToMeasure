from madetomeasure.schemas.organisation import OrganisationSchema
from madetomeasure.schemas.participants import EditParticipant
from madetomeasure.schemas.questions import AddQuestionSchema
from madetomeasure.schemas.questions import EditQuestionSchema
from madetomeasure.schemas.questions import TranslateQuestionSchema
from madetomeasure.schemas.root import EditSiteRoot
from madetomeasure.schemas.surveys import SurveySchema
from madetomeasure.schemas.surveys import SurveySectionSchema
from madetomeasure.schemas.surveys import SurveyInvitationSchema
from madetomeasure.schemas.surveys import SurveyReminderSchema
from madetomeasure.schemas.surveys import SurveyLangugageSchema
from madetomeasure.schemas.surveys import SurveyTranslate
from madetomeasure.schemas.surveys import SurveyClone
from madetomeasure.schemas.users import AddUserSchema
from madetomeasure.schemas.users import EditUserSchema
from madetomeasure.schemas.question_types import EditTextQuestionSchema
from madetomeasure.schemas.question_types import EditChoiceQuestionSchema
from madetomeasure.schemas.question_types import ChoiceSchema
from madetomeasure.schemas.system import LoginSchema

#FIXME: Replace with proper factories

CONTENT_SCHEMAS = {'AddQuestion':AddQuestionSchema,
                   'EditQuestion':EditQuestionSchema,
                   'TranslateQuestion':TranslateQuestionSchema,
                   'AddSurvey':SurveySchema,
                   'EditSurvey':SurveySchema,
                   'AddSurveySection':SurveySectionSchema,
                   'EditSurveySection':SurveySectionSchema,
                   'SurveyInvitation':SurveyInvitationSchema,
                   'AddUser':AddUserSchema,
                   'EditUser':EditUserSchema,
                   'AddOrganisation':OrganisationSchema,
                   'EditOrganisation':OrganisationSchema,
                   'SurveyReminder':SurveyReminderSchema,
                   'SurveyLangugage':SurveyLangugageSchema,
                   'EditParticipant':EditParticipant,
                   'EditSiteRoot':EditSiteRoot,
                   'TranslateSurvey':SurveyTranslate, 
                   'CloneSurvey':SurveyClone,
                   'EditTextQuestionType': EditTextQuestionSchema,
                   'EditChoiceQuestionType': EditChoiceQuestionSchema,
                   'AddChoice': ChoiceSchema,
                   'EditChoice': ChoiceSchema,
                   }

