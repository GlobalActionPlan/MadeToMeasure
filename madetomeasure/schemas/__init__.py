from madetomeasure.schemas.organisation import OrganisationSchema
from madetomeasure.schemas.questions import AddQuestionSchema
from madetomeasure.schemas.questions import EditQuestionSchema
from madetomeasure.schemas.surveys import SurveySchema
from madetomeasure.schemas.surveys import SurveySectionSchema
from madetomeasure.schemas.surveys import SurveyInvitationSchema
from madetomeasure.schemas.users import AddUserSchema
from madetomeasure.schemas.users import EditUserSchema

from madetomeasure.schemas.system import LoginSchema


CONTENT_SCHEMAS = {'AddQuestion':AddQuestionSchema,
                   'EditQuestion':EditQuestionSchema,
                   'AddSurvey':SurveySchema,
                   'EditSurvey':SurveySchema,
                   'AddSurveySection':SurveySectionSchema,
                   'EditSurveySection':SurveySectionSchema,
                   'SurveyInvitation':SurveyInvitationSchema,
                   'AddUser':AddUserSchema,
                   'EditUser':EditUserSchema,
                   'AddOrganisation':OrganisationSchema,
                   'EditOrganisation':OrganisationSchema,}

