from decimal import Decimal
from uuid import uuid4
from copy import deepcopy

from BTrees.OOBTree import OOBTree
from zope.interface import implements
from zope.component import getUtility
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.url import resource_url
from pyramid.exceptions import Forbidden
from pyramid.traversal import find_interface
from pyramid.traversal import find_root
from pyramid.renderers import render
from pyramid.interfaces import ISettings
from betahaus.pyracont import BaseFolder
from betahaus.pyracont.decorators import content_factory

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import ISurvey
from madetomeasure.interfaces import ISurveys
from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure.models.participants import Participant
from madetomeasure.models.date_time_helper import utcnow
from madetomeasure.models.exceptions import SurveyUnavailableError
from madetomeasure.models.security_aware import SecurityAware
from madetomeasure.models.app import select_language


class Surveys(BaseFolder, SecurityAware):
    """ Container for Survey models """
    implements(ISurveys)
    content_type = 'Surveys'
    display_name = _(u"Surveys")
    allowed_contexts = () #Not manually addable


@content_factory('Survey')
class Survey(BaseFolder, SecurityAware):
    """ Survey model """
    implements(ISurvey)
    content_type = 'Survey'
    display_name = _(u"Survey")
    allowed_contexts = ('Surveys',)
    custom_accessors = {'time_zone': 'get_time_zone', 
                        'welcome_text': 'get_welcome_text', 
                        'finished_text': 'get_finished_text'}
    custom_mutators = {'available_languages': 'set_available_languages', 
                       'heading_translations': 'set_heading_translations',
                       'welcome_text': 'set_welcome_text', 
                       'finished_text': 'set_finished_text',}
    schemas = {'add': 'SurveySchema', 'edit': 'SurveySchema', 'invitation': 'SurveyInvitationSchema',
               'reminder': 'SurveyReminderSchema', 'language': 'SurveyLangugageSchema',
               'translate': 'SurveyTranslateSchema', 'clone': 'SurveyCloneSchema',
               'delete': 'SurveyDeleteSchema'}
    
    def __init__(self, data=None, **kwargs):
        """  Init Survey """
        super(Survey, self).__init__(data=data, **kwargs)

    def get_translated_title(self, key=None, default=u""):
        """ This is a special version of title, since it might have translations.
            The regular setter works though, since the translations are stored in heading_translations.
        """
        try:
            lang = select_language(self)
        except ValueError:
            lang = 'en'
        translations = self.get_field_value('heading_translations', {})
        if lang and lang in translations:
            return translations[lang]
        
        return self._field_storage.get('title', default)
    
    @property
    def translations(self):
        if not hasattr(self, '__translations__'):
            self.__translations__ = OOBTree()
        return self.__translations__
        
    def set_translation(self, type, lang, value):
        if type not in self.translations:
            self.translations[type] = OOBTree()
            
        self.translations[type][lang] = value
        
    def get_translation(self, type, lang):
        if type not in self.translations:
            return ""
        if lang not in self.translations[type]:
            return ""
        return self.translations[type][lang]

    def set_available_languages(self, value, key=None):
        #b/c compat + custom mutator to make value a tuple
        value = tuple(value)
        self.field_storage['available_languages'] = value

    def get_available_languages(self):
        #b/c compat
        return self.get_field_value('available_languages', default=())

    def set_heading_translations(self, value, key=None):
        """ This is only for the translations of the question, since the title is the base language.
            value here should be a dict with country codes as keys and questions as values.
            Any empty value should be removed before saving.
        """
        #b/c compat + clean input value
        for (k, v) in value.items():
            if not v.strip():
                del value[k]
        self.field_storage['heading_translations'] = value

    def get_welcome_text(self, lang=None, default=True, **kwargs):
        text = None
        if lang:
            text = self.get_translation('__welcome_text__', lang)
        
        if text:
            return text
            
        if not default:
            return ""
            
        return getattr(self, '__welcome_text__', '')

    def set_welcome_text(self, value, lang=None, **kwargs):
        if lang:
            self.set_translation('__welcome_text__', lang, value)
        else:
            self.__welcome_text__ = value

    def get_finished_text(self, lang=None, default=True, **kwargs):
        #FIXME: Usage of default is broken here!
        text = None
        if lang:
            text = self.get_translation('__finished_text__', lang)

        if text:
            return text

        if not default:
            return ""

        return getattr(self, '__finished_text__', '')
        
    def set_finished_text(self, value, lang=None, **kwargs):
        #FIXME: This method sets both translation and default. Is that correct?
        if lang:
            self.set_translation('__finished_text__', lang, value)
        else:
            self.__finished_text__ = value

    def get_time_zone(self, default=None, **kwargs):
        """ custom accessor that uses default_timezone from settings as standard value, unless overridden. """
        marker = object()
        tz = self._field_storage.get('time_zone', marker)
        if tz is marker:
            return getUtility(ISettings)['default_timezone']
        return tz

    @property
    def tickets(self):
        if not hasattr(self, '__tickets__'):
            self.__tickets__ = OOBTree()
        return self.__tickets__
        
    def create_ticket(self, email):
        for (ticket_uid, ticket_email) in self.tickets.items():
            if email == ticket_email:
                return ticket_uid
        ticket_uid = unicode(uuid4())
        self.tickets[ticket_uid] = email
        return ticket_uid

    def send_invitations(self, request, emails=(), subject=None, message=None):
        """ Send out invitations to any emails stored as invitation_emails.
            Creates a ticket that a survey participant will "claim" to start the survey.
            Also removes emails from invitation pool.
        """
        for email in emails:
            invitation_uid = self.create_ticket(email)
            self.send_invitation_email(request, email, invitation_uid, subject, message)
        
    def send_invitation_email(self, request, email, uid, subject, message):
        mailer = get_mailer(request)
        sender = self.get_field_value('from_address', '')
        response = {}
        response['access_link'] = "%sdo?uid=%s" % (resource_url(self, request), uid)
        response['message'] = message
        response['subject'] = subject
        body_html = render('../views/templates/survey_invitation_mail.pt', response, request = request)

        #Must contain link etc, so each mail must be unique
        msg = Message(subject = subject,
                      sender = sender and sender or None,
                      recipients = [email.strip()],
                      html = body_html)
        mailer.send(msg)

    def start_survey(self, request):
        """ Initiates survey.
            - Checks that the incoming uid is correct
            - Adds a participant if it doesn't exist
            - Set participation in a survey on the participant
            - Returns participant_uid (taken from GET or POST in the request)
        """

        participant_uid = request.params.get('uid')
        if not participant_uid in self.tickets:
            raise Forbidden("Invalid ticket")
        
        root = find_root(self)
        participants = root['participants']
        
        #Have this person participated before?
        participant_email = self.tickets[participant_uid]
        obj = participants.participant_by_ids(self.__name__, participant_uid)

        if obj is None:
            #This is a new participant. Add info
            obj = Participant(email = participant_email)
            participants[obj.uid] = obj
        
        #Add survey
        obj.add_survey(self.__name__, participant_uid)

        return participant_uid
        
    def get_participants_data(self):
        """Returns the participants with statistics on the survey
        """
        
        participants = []
        for (uid, email) in self.tickets.items():
            participant = {}
            
            participant['uid'] = uid
            participant['email'] = email
        
            response = 0
            questions = 0
            for section in self.values():
                response += len(section.response_for_uid(uid))
                questions += len(section.question_ids)
                
            if response != 0:
                participant['finished'] = Decimal(response) / Decimal(questions) * 100
            else:
                participant['finished'] = 0
                
            participants.append(participant)
        
        return participants

    def check_open(self):
        """ Check if survey is open. The following principles apply:
            Start date:
            - If it exist, it must be in the past
            - If none exist, it's assumed to be open
            End date:
            - If it exist, must be before end date
            - If none exist, it's assumed to never close. (You have to add one manually!)
        """
        now = utcnow()
        start_time = self.get_field_value('start_time', None)
        end_time = self.get_field_value('end_time', None)
        
        #Check if it has start time and is started
        if start_time and start_time > now:
            msg = u"Survey has not opened"
            raise SurveyUnavailableError(self, msg=msg, not_started=True)
        
        #Check if it has end time and that it hasn't passed
        if end_time and end_time < now:
            msg = u"Survey has ended"
            raise SurveyUnavailableError(self, msg=msg, ended=True)
        
        return True
        
    def untranslated_languages(self):
        trans_util = getUtility(IQuestionTranslations)
        
        # get available for survey
        available_languages = list(self.get_available_languages())
        # remove default language
        if trans_util.default_locale_name in available_languages:
            available_languages.remove(trans_util.default_locale_name)
            
        organisation = find_interface(self, IOrganisation)
        variants = organisation.variants
            
        languages = {}
        for language in available_languages:
            questions = []
            for section in self.values():
                for name in section.question_ids:
                    question = section.question_object_from_id(name)
                    if not language in question.get_question_text() or (name in variants and not language in variants[name]):
                        questions.append(question)
            if questions:
                languages[language] = {
                        'name': "%s (%s)" % (trans_util.title_for_code_default(language), trans_util.title_for_code(language)),
                        'questions': questions,
                    }

        return languages
        
    def untranslated_texts(self):
        trans_util = getUtility(IQuestionTranslations)
        
        # get available for survey
        available_languages = list(self.get_available_languages())
        # remove default language
        if trans_util.default_locale_name in available_languages:
            available_languages.remove(trans_util.default_locale_name)
            
        languages = {}
        for language in available_languages:
            if not self.get_welcome_text(lang=language) or not self.get_finished_text(lang=language):
                languages[language] = "%s (%s)" % (trans_util.title_for_code_default(language), trans_util.title_for_code(language))

        return languages
        
    @property
    def participant_language(self):
        if not hasattr(self, '__participant_language__'):
            self.__participant_language__ = OOBTree()
        return self.__participant_language__
        
    @property
    def get_language_participants(self):
        languages = {}
        for key in self.participant_language:
            if self.participant_language[key] not in languages:
                languages[self.participant_language[key]] = []
            languages[self.participant_language[key]].append(key)
        
        return languages
    
    def set_participant_language(self, participant_uid, language):
        self.participant_language[participant_uid] = language

    def get_participant_language(self, participant_uid):
        return self.participant_language.get(participant_uid, None)
        
    # clone survey
    def clone(self, title, destination):
        new_survey = deepcopy(self)
        new_survey.set_field_value('title', title)
        new_survey.set_field_value('uid', unicode(uuid4()))
        # remove start and time
        del new_survey.field_storage['start_time']
        del new_survey.field_storage['end_time']
        # remove participant languages
        new_survey.participant_language.clear()
        # remove invitation tickets
        new_survey.tickets.clear()

        # remove participant responses
        for section in new_survey.values():
            section.set_field_value('uid', unicode(uuid4()))
            del section.__responses__
            section.__responses__ = OOBTree()

        # place survey in destination
        root = find_root(self)
        if destination not in root:
            raise ValueError('No organisation with that name')

        surveys = root[destination]['surveys']
        name = new_survey.suggest_name(surveys)
        surveys[name] = new_survey

        return new_survey
