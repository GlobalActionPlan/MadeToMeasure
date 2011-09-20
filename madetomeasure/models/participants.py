from zope.interface import implements
from BTrees.OOBTree import OOBTree

from madetomeasure.models.base import BaseFolder
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *


class Participants(BaseFolder):
    """ Container for participant objects. """
    implements(IParticipants)
    content_type = 'Participants'
    display_name = _(u"Participants")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name

    def set_title(self, value):
        pass
    
    def participants_by_emails(self, emails):
        results = set()
        for obj in self.values():
            if obj.get_email() in emails:
                results.add(obj)
        return results

    def participant_by_ids(self, survey_uid, participant_uid):
        """ Return a participant that matches survey_uid and particpant_uid in that survey.
            Returns None if a participant doesn't exist.
            This method is used do check if someone has participated in a survey before.
        """
        for obj in self.values():
            if not IParticipant.providedBy(obj):
                continue
            if survey_uid in obj.surveys:
                if participant_uid in obj.surveys[survey_uid]:
                    return obj


class Participant(BaseFolder):
    """ A Participant is a light-weight user object. They're not meant to be able to login.
    """
    implements(IParticipant)
    content_type = 'Participant'
    display_name = _(u"Participant")
    allowed_contexts = ('Participants',) #Not manually addable

    def get_title(self):
        """ Participant don't have a title. This is so they show up in listings. """
        return self.get_email()

    def set_title(self, value):
        """ Particpant should never be able to set title. """
        pass

    def set_email(self, value):
        self.__email__ = value
    
    def get_email(self):
        return getattr(self, '__email__', '')
    
    @property
    def surveys(self):
        """ Surveys consist of survey_id (which is the __name__ paramterer of a survey)
            and the participant_uid that is stored in that surveys tickets.
        """
        if not hasattr(self, '__surveys__'):
            self.__surveys__ = OOBTree()
        return self.__surveys__

    def add_survey(self, survey_id, participant_uid):
        self.surveys[survey_id] = participant_uid
    