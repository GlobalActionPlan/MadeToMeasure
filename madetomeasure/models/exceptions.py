

class SurveyUnavailableError(Exception):
    """ Raised when a user tries to access a survey that is not yet opened or has closed. """
    
    def __init__(self, survey, msg=u'', ended=False, not_started=False):
        super(SurveyUnavailableError, self).__init__()
        self.survey = survey
        self.msg = msg
        self.ended = ended
        self.not_started = not_started

    def __str__(self): # pragma: no cover
        return repr(self.msg)
    
    def __repr__(self): # pragma: no cover
        return "<%s '%s'>" % (self.__class__.__module__, self.msg)