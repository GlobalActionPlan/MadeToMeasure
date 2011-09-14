from uuid import uuid4

import colander
import deform
from BTrees.OOBTree import OOBTree
from zope.interface import implements
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.url import resource_url
from pyramid.exceptions import Forbidden
from pyramid.traversal import find_root
from pyramid.renderers import render

from madetomeasure.models.base import BaseFolder
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *
from madetomeasure.models.participants import Participant


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
    
    def get_invitation_emails(self):
        return getattr(self, '__invitation_emails__', '')
    
    def set_invitation_emails(self, value):
        self.__invitation_emails__ = value

    def get_from_address(self):
        return getattr(self, '__from_address__', '')

    def set_from_address(self, value):
        self.__from_address__ = value

    def get_mail_message(self):
        return getattr(self, '__mail_message__', '')

    def set_mail_message(self, value):
        self.__mail_message__ = value

    def _extract_emails(self):
        results = set()
        for email in self.get_invitation_emails().splitlines():
            results.add(email.strip())
        return results
    
    @property
    def tickets(self):
        if not hasattr(self, '__tickets__'):
            self.__tickets__ = OOBTree()
        return self.__tickets__
        
    def create_ticket(self, email):
        ticket_uid = unicode(uuid4())
        self.tickets[ticket_uid] = email
        return ticket_uid

    def send_invitations(self, request, text=None):
        """ Send out invitations to any emails stored as invitation_emails.
            Creates a ticket that a survey participant will "claim" to start the survey.
            Also removes emails from invitation pool.
        """
        mailer = get_mailer(request)
        sender = self.get_from_address()
        
        for email in self._extract_emails():
            invitation_uid = self.create_ticket(email)
            
            response = {}
            response['message'] = u"A message" #FIXME
            response['access_link'] = "%sdo?uid=%s" % (resource_url(self, request), invitation_uid)
            body_html = render('../views/templates/survey_invitation_mail.pt', response, request=request)            

            #Must contain link etc, so each mail must be unique
            msg = Message(subject=_(u"Survey invitation"),
                          sender = sender and sender or None,
                          recipients=[email],
                          html=body_html)

            mailer.send(msg)
            
        self.set_invitation_emails('') #Blank out emails, since we've already sent them

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
        result = tuple(participants.participants_by_emails((participant_email,)))
        if len(result) == 1:
            #This participant has participated in another survey. Update information
            obj = result[0]
        elif not result:
            #This is a new participant. Add info
            obj = Participant()
            obj.set_email(participant_email) #Fetches email
            participants[unicode(uuid4())] = obj
        else:
            raise ValueError("A single email address returned several users. Email was: %s" % participant_email)
        
        #Add survey
        obj.add_survey(self.__name__, participant_uid)
        
        return participant_uid


class SurveySection(BaseFolder):
    implements(ISurveySection)
    content_type = 'SurveySection'
    display_name = _(u"Survey Section")
    allowed_contexts = ('Survey',)

    def get_question_type(self):
        return getattr(self, '__question_type__', '')
    
    def set_question_type(self, value):
        self.__question_type__ = value

    def get_question_ids(self):
        return getattr(self, '__question_ids__', set())

    def set_question_ids(self, value):
        self.__question_ids__ = value
    
    def append_questions_to_schema(self, schema):
        """ Append all questions to a schema. """
        root = find_root(self)
        questions = root['questions']
        lang = None #FIXME:

        for id in self.get_question_ids():
            question = questions[id]
            schema.add(question.question_schema_node(id))

    @property
    def responses(self):
        if not hasattr(self, '__responses__'):
            self.__responses__ = OOBTree()
        return self.__responses__
        
    def update_question_responses(self, participant_uid, responses):
        self.responses[participant_uid] = responses

    def response_for_uid(self, participant_uid):
        return self.responses.get(participant_uid, {})
