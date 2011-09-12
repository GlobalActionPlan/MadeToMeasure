from hashlib import sha1
from BTrees.OOBTree import OOBTree

import colander
from repoze.folder import Folder
from zope.interface import implements

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import *
from madetomeasure.schemas import QUESTION_SCHEMAS


def appmaker(zodb_root):
    if not 'app_root' in zodb_root:
        app_root = bootstrap_root()
        zodb_root['app_root'] = app_root
        import transaction
        transaction.commit()
    return zodb_root['app_root']


def bootstrap_root():
    root = SiteRoot()
    root['users'] = Users()
    #Create admin user with password admin as standard
    admin = User()
    admin.set_password('admin')
    admin.set_title('Administrator')
    root['users']['admin'] = admin
    
    root['surveys'] = Surveys()
    root['participants'] = Participants()
    root['questions'] = Questions()
    
    return root


def get_sha_password(password):
    """ Encode a plaintext password to sha1. """
    if isinstance(password, unicode):
        password = password.encode('UTF-8')
    return 'SHA1:' + sha1(password).hexdigest()


class SiteRoot(Folder):
    implements(ISiteRoot)
    content_type = 'SiteRoot'
    display_name = _(u"Site root")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name

class Users(Folder):
    """ Container for system users. These are translators, managers
        or any other folks that need to login.
    """
    implements(IUsers)
    content_type = 'Users'
    display_name = _(u"Users")
    allowed_contexts = () #Not manually addable
    
    def get_title(self):
        return self.display_name


class User(Folder):
    """ A system user """
    implements(IUser)
    content_type = 'User'
    display_name = _(u"User")
    allowed_contexts = ('Users',)
    
    @property
    def userid(self):
        return self.__name__
    
    def set_title(self, value):
        self.__title__ = value
    
    def get_title(self):
        return getattr(self, '__title__', '')
    
    def set_email(self, value):
        self.__email__ = value
    
    def get_email(self):
        return getattr(self, '__email__', '')

    def set_password(self, value):
        self.__password__ = get_sha_password(value)
    
    def check_password(self, value):
        """ Check a plaintext password against stored encrypted password. """
        hash = get_sha_password(value)
        return hash == self.get_password()

    def get_password(self):
        return self.__password__
    

class Surveys(Folder):
    implements(ISurveys)
    content_type = 'Surveys'
    display_name = _(u"Surveys")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name

class Survey(Folder):
    implements(ISurvey)
    content_type = 'Survey'
    display_name = _(u"Survey")
    allowed_contexts = ('Surveys',)


class Participants(Folder):
    """ Container for participant objects. """
    implements(IParticipants)
    content_type = 'Participants'
    display_name = _(u"Participants")
    allowed_contexts = () #Not manually addable

    def get_title(self):
        return self.display_name
    

class Participant(Folder):
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


class Questions(Folder):
    implements(IQuestions)
    content_type = 'Questions'
    display_name = _(u"Questions")
    allowed_contexts = () #Not manually addable
    
    def get_title(self):
        return self.display_name


class Question(Folder):
    implements(IQuestion)
    content_type = 'Question'
    display_name = _(u"Question")
    allowed_contexts = ('Questions', )

    def __init__(self):
        self.__question_text__ = OOBTree()
        self.__question_type_schema__ = ''
        super(Question, self).__init__()
    
    def get_title(self):
        return getattr(self, '__title__', '')
    
    def set_title(self, value):
        self.__title__ = value
    
    def get_question_text(self):
        results = []
        for (lang, text) in self.__question_text__.items():
            results.append({'lang':lang,'text':text})
        return results

    def set_question_text(self, value):
        """ Example value: [{'lang': u'sv', 'text': u'Svensk text'}] """
        new_keys = [x['lang'] for x in value]
        for entry in value:
            self.__question_text__[entry['lang']] = entry['text']
        #Remove any keys not present in the form. They've been deleted
        for k in self.__question_text__.keys():
            if k not in new_keys:
                del self.__question_text__[k]
    
    def get_question_type_schema(self):
        return self.__question_type_schema__
    
    def set_question_type_schema(self, value):
        self.__question_type_schema__ = value

    def get_schema(self, lang):
        """ Get a question schema with 'text' as the translated text of the question. """
        title = self.__question_text__.get(lang, None)
        if title is None:
            title = self.get_title()
        schema_type = self.get_question_type_schema()
        if schema_type not in QUESTION_SCHEMAS:
            raise KeyError("There's no schema called %s in QUESTION_SCHEMAS" % schema_type)
        return QUESTION_SCHEMAS[schema_type]().bind(question_title = title)


CONTENT_TYPES = {'User':User,
                 'Survey':Survey,
                 'Participant':Participant,
                 'Question':Question,
                 }