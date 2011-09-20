

class SurveyUnavailableError(Exception):
    """ Raised when a user tries to access a survey that is not yet opened or has closed. """
    
    def __init__(self, survey, msg=u''):
        super(SurveyUnavailableError, self).__init__()
        self.survey = survey
        self.msg = msg