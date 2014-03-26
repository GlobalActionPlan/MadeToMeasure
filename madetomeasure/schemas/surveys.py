from operator import itemgetter

import colander
import deform
from zope.component import getUtility
from betahaus.pyracont.decorators import schema_factory

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.common import deferred_available_languages_widget
from madetomeasure.schemas.common import deferred_delete_title
from madetomeasure.schemas.common import time_zone_node
from madetomeasure.schemas.validators import deferred_confirm_delete_with_title_validator
from madetomeasure.schemas.validators import multiple_email_validator
from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure.security import EDIT
from madetomeasure.security import context_has_permission


def survey_heading_translations_node():
    return colander.Schema(title=_("Survey heading translations"),
                           description=_(u"survey_heading_translation_description",
                                         default = u"For each language - but will not be available until the languages have been set and saved!")) #Send this to add_translations_schema

def section_heading_translations_node():
    return colander.Schema(title=_("Section heading translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema

def section_description_translations_node():
    return colander.Schema(title=_("Section description translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema


@schema_factory('SurveySchema')
class SurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _(u"Title"),)
    heading_translations = survey_heading_translations_node()
    from_address = colander.SchemaNode(colander.String(),
                                       title = _(u"Email to send system mail from"),
                                       validator=colander.Email(),)
    time_zone = time_zone_node()
    available_languages = colander.SchemaNode(colander.Set(),
                                              widget=deferred_available_languages_widget,
                                              title=_("Available languages"),)
    allow_anonymous_to_participate = colander.SchemaNode(colander.Bool(),
        title = _(u"allow_anonymous_to_participate_title",
                  default = u"Allow anonymous people to participate in the survey?"),
        description = _(u"allow_anonymous_to_participate_description",
                        default = u"When someone reaches the survey link, allow them to enter "
                            u"their email address to get an invitation and participate in the survey."),
        missing = False,
    )
    allow_anonymous_to_start = colander.SchemaNode(colander.Bool(),
        title = _(u"allow_anonymous_to_start_title",
                  default = u"Allow anonymous people to start the survey without validating their email."),
        description = _(u"allow_anonymous_to_start_description",
                        default = u"Last resort - only allow this if there's major email problems with outgoing email!"),
        missing = False,
    )


@schema_factory('SurveySectionSchema')
class SurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _(u"Title"),
                                widget=deform.widget.TextInputWidget(size=80))
    heading_translations = section_heading_translations_node()
    description = colander.SchemaNode(colander.String(),
                                      title = _(u"Description"),
                                      widget=deform.widget.RichTextWidget(),
                                      missing=u"",)
    description_translations = section_description_translations_node()


@schema_factory('TextSectionSchema')
class TextSectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    description = colander.SchemaNode(colander.String(),
                                      widget = deform.widget.RichTextWidget(),
                                      missing = u"",)


@colander.deferred
def deferred_delete_survey_section_desc(node, kw):
    context = kw['context']
    if len(context.responses):
        return _(u"WARNING! This section has response data. If you delete it, it will be lost forever!")
    return u""


@schema_factory('DeleteSurveySectionSchema', title = _(u"Really delete object?"), description = deferred_delete_survey_section_desc)
class DeleteSurveySectionSchema(colander.Schema):
    confirm = colander.SchemaNode(colander.String(),
                                  title = deferred_delete_title,
                                  validator = deferred_confirm_delete_with_title_validator,)


@schema_factory('SurveyDeleteSchema', title = _(u"Really delete this survey?"),
                description = _(u"WARNING: There's no undo if you do this!"))
class SurveyDeleteSchema(colander.Schema):
    confirm = colander.SchemaNode(colander.String(),
                                  title = deferred_delete_title,
                                  validator = deferred_confirm_delete_with_title_validator,)


@schema_factory('SurveyInvitationSchema')
class SurveyInvitationSchema(colander.Schema):
    subject = colander.SchemaNode(colander.String(),
                                  title = _(u"Email subject and text header"),
                                  description = _(u"Will be visible in the subject line, and as a header in the email body."))
    message = colander.SchemaNode(colander.String(),
                                  title = _(u"Message - please note that the link will be added as a new line below the message!"),
                                  widget = deform.widget.RichTextWidget(),
                                  default = _(u'Please fill in the survey. Click the link below to access it:'),)
    emails = colander.SchemaNode(colander.String(),
                                 title = _(u"Participant email addresses - add one per row."),
                                 description = _(u"invitation_emails_lang_notice",
                                                 default = u"Remember to only add users who should recieve the message in this language."),
                                 validator = multiple_email_validator,
                                 widget=deform.widget.TextAreaWidget(rows=10, cols=50),)


@colander.deferred
def deferred_participant_actions(node, kw):
    request = kw['request']
    context = kw['context']
    choices = []
    if context.get_field_value('allow_anonymous_to_participate', False):
        choices.append((u'send_anon_invitation', _(u"I want to participate in the survey - send me a link.")))
    choices.append((u'resend_access', _(u"I lost my access link - send me a new one.")))
    if context.get_field_value('allow_anonymous_to_start', False):
        choices.append((u'start_anon', _(u"Start my survey without verifying my email.")))
    return deform.widget.RadioChoiceWidget(values = choices)


@schema_factory('ParticipantControlsSchema')
class ParticipantControlsSchema(colander.Schema):
    email = colander.SchemaNode(colander.String(),
                                title = _(u"Your email"),
                                validator = colander.Email())
    participant_actions = colander.SchemaNode(colander.String(),
                                              title = _(u"Actions"),
                                              widget = deferred_participant_actions,)


@schema_factory('SurveyReminderSchema')
class SurveyReminderSchema(colander.Schema):
    subject = colander.SchemaNode(colander.String(),
                                  title = _(u"Email subject and text header"),
                                  description = _(u"Will be visible in the subject line, and as a header in the email body."))
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
    return deform.widget.RadioChoiceWidget(values=choices)


@schema_factory('SurveyLangugageSchema')
class SurveyLangugageSchema(colander.Schema):
    selected_language = colander.SchemaNode(colander.String(),
                                          title=_("Choose language"),
                                          widget=deferred_select_language_widget,)


def _valid_organisaitons(root, userid):
    results = []
    for obj in root.values():
        if IOrganisation.providedBy(obj) and context_has_permission(obj, EDIT, userid):
            results.append(obj)
    return sorted(results, key = lambda x: x.title.lower())


class OrganisationValidator(object):
    def __init__(self, view):
        self.view = view
    
    def __call__(self, node, value):
        #Value here is the destination __name__
        org_names = [x.__name__ for x in _valid_organisaitons(self.view.root, self.view.userid)]
        if value not in org_names:
            raise colander.Invalid(node, _(u"Invalid target organisation"))


@colander.deferred
def survey_clone_destination_validator(node, kw):
    view = kw['view']
    return OrganisationValidator(view)


@colander.deferred
def survey_clone_destination_widget(node, kw):
    view = kw['view']
    choices = []
    for organisation in _valid_organisaitons(view.root, view.userid):
        choices.append((organisation.__name__, organisation.title))
    return deform.widget.SelectWidget(values = choices)


@schema_factory('SurveyCloneSchema')
class SurveyCloneSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _(u"Title"),)
    destination = colander.SchemaNode(colander.String(),
                                      title = _(u"Destination"),
                                      widget=survey_clone_destination_widget,
                                      validator=survey_clone_destination_validator,)
