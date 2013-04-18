from operator import itemgetter

import colander
import deform
from pyramid.security import has_permission
from pyramid.traversal import find_root
from zope.component import getUtility

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.common import deferred_available_languages_widget
from madetomeasure.schemas.common import time_zone_node
from madetomeasure.schemas.validators import multiple_email_validator
from madetomeasure.interfaces import IOrganisation
from madetomeasure.models.fields import TZDateTime
from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure.security import EDIT


def survey_heading_translations_node():
    return colander.Schema(title=_("Survey heading translations"),
                           description=_(u"For each language - but will not be available until the languages have been set and saved!")) #Send this to add_translations_schema

def survey_welcome_translations_node():
    return colander.Schema(title=_("Survey welcome translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema
                           
def survey_finished_translations_node():
    return colander.Schema(title=_("Survey finished translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema

def section_heading_translations_node():
    return colander.Schema(title=_("Section heading translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema

def section_description_translations_node():
    return colander.Schema(title=_("Section description translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema


class SurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    heading_translations = survey_heading_translations_node()
    start_time = colander.SchemaNode(
         TZDateTime(),
         title = _(u"Start time for survey"),
         missing=colander.null,
         widget=deform.widget.DateTimeInputWidget(options={'dateFormat': 'yy-mm-dd',
                                                           'timeFormat': 'hh:mm',
                                                           'separator': ' '}),
    )
    end_time = colander.SchemaNode(
         TZDateTime(),
         title = _(u"End time for survey"),
         missing=colander.null,
         widget=deform.widget.DateTimeInputWidget(options={'dateFormat': 'yy-mm-dd',
                                                           'timeFormat': 'hh:mm',
                                                           'separator': ' '}),
    )
    from_address = colander.SchemaNode(colander.String(),
                                       validator=colander.Email(),)
    welcome_text = colander.SchemaNode(colander.String(),
                                        widget=deform.widget.RichTextWidget(),
                                        missing=u"",)
    finished_text = colander.SchemaNode(colander.String(),
                                        widget=deform.widget.RichTextWidget(),
                                        default=_(u"Thanks a lot for filling out the survey."),)
    time_zone = time_zone_node()
    available_languages = colander.SchemaNode(deform.Set(),
                                              widget=deferred_available_languages_widget,
                                              title=_("Available languages"),)


class SurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                widget=deform.widget.TextInputWidget(size=80))
    heading_translations = section_heading_translations_node()
    description = colander.SchemaNode(colander.String(),
                                      widget=deform.widget.RichTextWidget(),
                                      missing=u"",)
    description_translations = section_description_translations_node()


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


class SurveyLangugageSchema(colander.Schema):
    selected_language = colander.SchemaNode(colander.String(),
                                          title=_("Choose language"),
                                          widget=deferred_select_language_widget,)


class SurveyTranslate(colander.Schema):
    welcome_text = colander.SchemaNode(colander.String(),
                                        widget=deform.widget.RichTextWidget(),
                                        default="",
                                        missing="",)
    finished_text = colander.SchemaNode(colander.String(),
                                        widget=deform.widget.RichTextWidget(),
                                        default="",
                                        missing="",)


class OrganisationValidator(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self, node, value):
        root = find_root(self.context)
        destination = value

        invalid = False

        try:
            organisation = root[destination]
        except KeyError:
            invalid = True
        else:
            if not (IOrganisation.providedBy(organisation) and has_permission(EDIT, organisation, self.request)):
                invalid = True

        if invalid:
            raise colander.Invalid(node, 'Not a valid organisation')


@colander.deferred
def survey_clone_destination_validator(form, kw):
    context = kw['context']
    request = kw['request']
    return OrganisationValidator(context, request)


@colander.deferred
def survey_clone_destination_widget(node, kw):
    context = kw['context']
    request = kw['request']
    
    root = find_root(context)
    choices=set()
    for organisation in root.values():
        if IOrganisation.providedBy(organisation) and has_permission(EDIT, organisation, request):
            choices.add((organisation.__name__, organisation.get_field_value('title')))

    return deform.widget.SelectWidget(values=choices)


class SurveyClone(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    destination = colander.SchemaNode(colander.String(),
                                      widget=survey_clone_destination_widget,
                                      validator=survey_clone_destination_validator,)
