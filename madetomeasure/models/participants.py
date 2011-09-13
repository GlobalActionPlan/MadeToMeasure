from zope.interface import implements

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
    

class Participant(BaseFolder):
    """ A Participant is a light-weight user object. They're not meant to be able to login.
    """
    implements(IParticipant)
    content_type = 'Participant'
    display_name = _(u"Participant")
    allowed_contexts = ('Participants',) #Not manually addable

    def set_email(self, value):
        self.__email__ = value
    
    def get_email(self):
        return getattr(self, '__email__', '')

