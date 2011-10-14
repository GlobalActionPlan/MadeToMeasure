from decimal import Decimal
from uuid import uuid4
from copy import copy

import colander
import deform
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

from madetomeasure.models.base import BaseFolder
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *
from madetomeasure.models.participants import Participant
from madetomeasure.models.date_time_helper import utcnow
from madetomeasure.models.exceptions import SurveyUnavailableError
from madetomeasure.models.app import select_language


class Surveys(BaseFolder):
    implements(ISurveys)
    content_type = 'Surveys'
    display_name = _(u"Surveys")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name

    def set_title(self, value):
        pass


class Survey(BaseFolder):
    implements(ISurvey)
    content_type = 'Survey'
    display_name = _(u"Survey")
    allowed_contexts = ('Surveys',)
    
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

    def get_from_address(self):
        return getattr(self, '__from_address__', '')

    def set_from_address(self, value):
        self.__from_address__ = value

    def set_available_languages(self, value):
        self.__available_languages__ = value
        
    def get_available_languages(self):
        return getattr(self, '__available_languages__', ())

    def get_welcome_text(self, lang=None, default=True):
        text = None
        if lang:
            text = self.get_translation('__welcome_text__', lang)
        
        if text:
            return text
            
        if not default:
            return ""
            
        return getattr(self, '__welcome_text__', '')

    def set_welcome_text(self, value, lang=None):
        if lang:
            self.set_translation('__welcome_text__', lang, value)
        
        self.__welcome_text__ = value

    def get_finished_text(self, lang=None, default=True):
        text = None
        if lang:
            text = self.get_translation('__finished_text__', lang)
        
        if text:
            return text
            
        if not default:
            return ""
            
        return getattr(self, '__finished_text__', '')
        
    def set_finished_text(self, value, lang=None):
        if lang:
            self.set_translation('__finished_text__', lang, value)
        
        self.__finished_text__ = value

    def get_start_time(self):
        return getattr(self, '__start_time__', None)

    def set_start_time(self, value):
        self.__start_time__ = value

    def get_end_time(self):
        return getattr(self, '__end_time__', None)

    def set_end_time(self, value):
        self.__end_time__ = value

    def get_time_zone(self):
        tz = getattr(self, '__time_zone__', None)
        if tz is None:
            return getUtility(ISettings)['default_timezone']
        return tz

    def set_time_zone(self, value):
        self.__time_zone__ = value
    
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

    def send_invitations(self, request, emails=(), message=None):
        """ Send out invitations to any emails stored as invitation_emails.
            Creates a ticket that a survey participant will "claim" to start the survey.
            Also removes emails from invitation pool.
        """
        for email in emails:
            invitation_uid = self.create_ticket(email)
            self.send_invitation_email(request, email, invitation_uid, message)
        
    def send_invitation_email(self, request, email, uid, message):
        mailer = get_mailer(request)
        sender = self.get_from_address()

        response = {}
        response['message'] = message
        response['access_link'] = "%sdo?uid=%s" % (resource_url(self, request), uid)
        body_html = render('../views/templates/survey_invitation_mail.pt', response, request=request)

        #Must contain link etc, so each mail must be unique
        msg = Message(subject=_(u"Survey invitation"),
                      sender = sender and sender or None,
                      recipients=[email],
                      html=body_html)

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
            obj = Participant()
            obj.set_email(participant_email) #Fetches email
            participants[unicode(uuid4())] = obj
        
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

    def structured_global_question_objects(self):
        root = find_root(self)
        questions = root['questions']
        results = {}
        for question in questions.values():
            if not IQuestion.providedBy(question):
                continue
            type = question.get_question_type()
            if type not in results:
                results[type] = []
            results[type].append(question)
        return results

    def add_structured_question_choices(self, schema):
        """ Append all selectable questions to a schema.
        """
        questions = self.structured_global_question_objects()

        for (type, questions) in questions.items():
            choices = [(x.__name__, x.get_title()) for x in questions]
            schema.add(colander.SchemaNode(deform.Set(allow_empty=True),
                                           name=type,
                                           widget=deform.widget.CheckboxChoiceWidget(values=choices),),
                                           )

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
        start_time = self.get_start_time()
        end_time = self.get_end_time()
        
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
        available_languages = copy(self.get_available_languages())
        # remove default language
        if trans_util.default_locale_name in available_languages:
            available_languages.remove(trans_util.default_locale_name)
            
        organisation = find_interface(self, IOrganisation)
        invariants = organisation.invariants
            
        languages = {}
        for language in available_languages:
            questions = []
            for section in self.values():
                for name in section.question_ids:
                    question = section.question_object_from_id(name)
                    if not language in question.get_question_text() or (name in invariants and not language in invariants[name]):
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
        available_languages = copy(self.get_available_languages())
        # remove default language
        if trans_util.default_locale_name in available_languages:
            available_languages.remove(trans_util.default_locale_name)
            
        languages = {}
        for language in available_languages:
            if not self.get_welcome_text(lang=language) or not self.get_finished_text(lang=language):
                languages[language] = "%s (%s)" % (trans_util.title_for_code_default(language), trans_util.title_for_code(language))

        return languages

class SurveySection(BaseFolder):
    implements(ISurveySection)
    content_type = 'SurveySection'
    display_name = _(u"Survey Section")
    allowed_contexts = ('Survey',)
    
    def get_title(self):
        """ This is a special version of get title, since it might have translations.
            The regular setter works though, since the translations are stored in heading_translations.
        """
        lang = select_language(self)
        translations = self.get_heading_translations()
        if lang and lang in translations:
            return translations[lang]
        
        return getattr(self, '__title__', '')
    
    @property
    def question_ids(self):
        uids = set()
        for v in self.get_structured_question_ids().values():
            uids.update(v)
        
        order = self.get_order()
        for v in uids:
            if not v in order:
                order.append(v)
        
        return order
        
    def get_order(self):
        return getattr(self, '__order__', [])
            
    def set_order(self, value):
        uids = set()
        for v in self.get_structured_question_ids().values():
            uids.update(v)
            
        order = []
        for v in value:
            if v in uids:
                order.append(v)
        
        self.__order__ = order

    def get_question_type(self):
        return getattr(self, '__question_type__', '')
    
    def set_question_type(self, value):
        self.__question_type__ = value

    def get_heading_translations(self):
        return getattr(self, '__heading_translations__', {})

    def set_heading_translations(self, value):
        """ This is only for the translations of the question, since the title is the base language.
            value here should be a dict with country codes as keys and questions as values.
            Any empty value should be removed before saving.
        """
        for (k, v) in value.items():
            if not v.strip():
                del value[k]
        self.__heading_translations__ = value

    def get_structured_question_ids(self):
        return getattr(self, '__structured_question_ids__', {})

    def set_structured_question_ids(self, value):
        """ value format {'question_type_id': [question_uid, question_uid]} """
        self.__structured_question_ids__ = value

    def append_questions_to_schema(self, schema, request):
        """ Append all questions to a schema. """
        
        lang = None
        if 'lang' in request.session:
            lang = request.session['lang']
 
        for id in self.question_ids:
            question = self.question_object_from_id(id)
            schema.add(question.question_schema_node(id, lang=lang, context=self))

    @property
    def responses(self):
        if not hasattr(self, '__responses__'):
            self.__responses__ = OOBTree()
        return self.__responses__
        
    def update_question_responses(self, participant_uid, responses):
        self.responses[participant_uid] = responses

    def response_for_uid(self, participant_uid):
        return self.responses.get(participant_uid, {})

    def question_object_from_id(self, id):
        """ id is the same as the Question __name__ attribute.
            Will raise KeyError if not found.
            Will global question pool but IDs shouldn't be the same
            anyway so that's probably not a concern
        """
        root = find_root(self)
        try:
            return root['questions'][id]
        except KeyError:
            org = find_interface(self, IOrganisation)
            return org['questions'][id]

    def question_format_results(self):
        """ Return a structure suitable for looking up responses for each question.
        """
        results = OOBTree()
        
        for response in self.responses.values():
            for (k, v) in response.items():
                if k not in results:
                    results[k] = []
                results[k].append(v)
        return results
