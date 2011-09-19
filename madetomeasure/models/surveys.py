from decimal import Decimal
from uuid import uuid4

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

    def get_finished_text(self):
        return getattr(self, '__finished_text__', '')

    def set_finished_text(self, value):
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
        for (ticket_uid, ticket_email) in self.tickets.items():
            if email == ticket_email:
                return ticket_uid
        ticket_uid = unicode(uuid4())
        self.tickets[ticket_uid] = email
        return ticket_uid

    def send_invitations(self, request, text=None):
        """ Send out invitations to any emails stored as invitation_emails.
            Creates a ticket that a survey participant will "claim" to start the survey.
            Also removes emails from invitation pool.
        """
        for email in self._extract_emails():
            invitation_uid = self.create_ticket(email)
            
            message = u"A message" #FIXME
            self.send_invitation_email(request, email, invitation_uid, message)
            
        self.set_invitation_emails('') #Blank out emails, since we've already sent them
        
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


    def structured_local_question_objects(self):
        org = find_interface(self, IOrganisation)
        questions = org['questions']
        results = {}
        for question in questions.values():
            if not IQuestion.providedBy(question):
                continue
            type = question.get_question_type()
            if type not in results:
                results[type] = []
            results[type].append(question)
        return results
    
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
        questions.update(self.structured_local_question_objects())

        for (type, questions) in questions.items():
            choices = [(x.__name__, x.get_title()) for x in questions]
            schema.add(colander.SchemaNode(deform.Set(allow_empty=True),
                                           name=type,
                                           widget=deform.widget.CheckboxChoiceWidget(values=choices),),
                                           )



class SurveySection(BaseFolder):
    implements(ISurveySection)
    content_type = 'SurveySection'
    display_name = _(u"Survey Section")
    allowed_contexts = ('Survey',)
    
    @property
    def question_ids(self):
        results = set()
        for v in self.get_structured_question_ids().values():
            results.update(v)
        return results

    def get_question_type(self):
        return getattr(self, '__question_type__', '')
    
    def set_question_type(self, value):
        self.__question_type__ = value

    def get_structured_question_ids(self):
        return getattr(self, '__structured_question_ids__', {})

    def set_structured_question_ids(self, value):
        self.__structured_question_ids__ = value

    def append_questions_to_schema(self, schema):
        """ Append all questions to a schema. """
        lang = None #FIXME
 
        for id in self.question_ids:
            question = self.question_object_from_id(id)
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
    
