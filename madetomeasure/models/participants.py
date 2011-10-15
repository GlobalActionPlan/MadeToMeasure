from zope.interface import implements
from BTrees.OOBTree import OOBTree
from betahaus.pyracont import BaseFolder

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IParticipant
from madetomeasure.interfaces import IParticipants
from madetomeasure.models.security_aware import SecurityAware


class Participants(BaseFolder, SecurityAware):
    """ Container for participant objects. """
    implements(IParticipants)
    content_type = 'Participants'
    display_name = _(u"Participants")
    allowed_contexts = () #Not manually addable
    
    def participants_by_emails(self, emails):
        results = set()
        for obj in self.values():
            if obj.get_field_value('email', '') in emails:
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


class Participant(BaseFolder, SecurityAware):
    """ A Participant is a light-weight user object. They're not meant to be able to login.
    """
    implements(IParticipant)
    content_type = 'Participant'
    display_name = _(u"Participant")
    allowed_contexts = ('Participants',) #Not manually addable
    custom_accessors = {'title': 'get_title'}
    custom_mutators = {'title': 'set_title'}

    def __init__(self, data=None, **kwargs):
        """  Init Participant """
        super(Participant, self).__init__(data=data, **kwargs)
        self.__surveys__ = OOBTree()

    def get_title(self, default='', key=None):
        """ Participant don't have a title. This is so they show up in listings. """
        return self.get_field_value('email', default)

    def set_title(self, value, **kwargs):
        """ Particpant should never be able to set title. """
        pass

    @property
    def surveys(self):
        """ Surveys consist of survey_id (which is the __name__ paramterer of a survey)
            and the participant_uid that is stored in that surveys tickets.
        """
        return self.__surveys__

    def add_survey(self, survey_id, participant_uid):
        self.surveys[survey_id] = participant_uid
    