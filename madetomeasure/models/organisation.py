from BTrees.OOBTree import OOBTree
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import DENY_ALL
from pyramid.traversal import find_root
from zope.interface import implements
from betahaus.pyracont import BaseFolder
from betahaus.pyracont.decorators import content_factory

from madetomeasure.interfaces import IOrganisation
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure import security
from madetomeasure.models.security_aware import SecurityAware


@content_factory('Organisation')
class Organisation(BaseFolder, SecurityAware):
    implements(IOrganisation)
    content_type = 'Organisation'
    display_name = _(u"Organisation")
    allowed_contexts = ('SiteRoot',)
    schemas = {'add': 'OrganisationSchema', 'edit': 'OrganisationSchema'}

    __acl__ = [(Allow, security.ROLE_ADMIN, ALL_PERMISSIONS),
               (Allow, security.ROLE_ORGANISATION_MANAGER, ALL_PERMISSIONS),
               DENY_ALL,
              ]
    
    def __init__(self, data=None, **kwargs):
        """ Bootstrap an organisation """
        super(Organisation, self).__init__(data=data, **kwargs)
        #FIXME: Should be done by factories instead
        from madetomeasure.models.surveys import Surveys
        self['surveys'] = Surveys()
        from madetomeasure.models.questions import LocalQuestions
        self['questions'] = LocalQuestions()

    @property
    def variants(self):
        try:
            return self.__variants__
        except AttributeError:
            self.__variants__ = OOBTree()
            return self.__variants__
        
    def get_variant(self, question_name, lang):
        """ Returns variant of question for language if there is one """
        if question_name in self.variants:
            if lang in self.variants[question_name]:
                return self.variants[question_name][lang]
        return None
        
    def set_variant(self, question_name, lang, value):
        # with an empty value remove the variant
        if not value.strip():
            if question_name in self.variants and lang in self.variants[question_name]:
                del self.variants[question_name][lang]
        else:
            if not question_name in self.variants:
                self.variants[question_name] = OOBTree()
            self.variants[question_name][lang] = value

    @property
    def questions(self):
        root = find_root(self)
        questions = dict(root['questions'].items())
        questions.update(dict(self['questions'].items()))
        return questions
