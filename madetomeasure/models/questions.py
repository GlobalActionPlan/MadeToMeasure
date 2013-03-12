from zope.interface import implements
from BTrees.OOBTree import OOBTree
from zope.component import getUtility
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_interface
from betahaus.pyracont import BaseFolder
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import DENY_ALL

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure import security
from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IQuestion
from madetomeasure.interfaces import IQuestions
from madetomeasure.interfaces import IQuestionNode
from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure.models.security_aware import SecurityAware


class Questions(BaseFolder, SecurityAware):
    """ Question container """
    implements(IQuestions)
    content_type = 'Questions'
    display_name = _(u"Questions")
    allowed_contexts = ()

    __acl__ = [(Allow, security.ROLE_ADMIN, ALL_PERMISSIONS),
               (Allow, security.ROLE_TRANSLATOR, (security.TRANSLATE, security.VIEW)),
               DENY_ALL]

    def questions_by_type(self, question_type):
        """ Return available question objects according to a specific type. """
        results = set()
        for obj in self.values():
            if not IQuestion.providedBy(obj):
                continue
            if obj.get_question_type() == question_type:
                results.add(obj)
        return results


class Question(BaseFolder, SecurityAware):
    """ Question model """
    implements(IQuestion)
    content_type = 'Question'
    display_name = _(u"Question")
    allowed_contexts = ('Questions', )
    custom_accessors = {'title': 'get_title',
                        'question_text': 'get_question_text',
                        'tags': '_get_tags'}
    custom_mutators = {'question_text': 'set_question_text',
                       'tags': '_set_tags',}

    def __init__(self, data = None, **kwargs):
        self.__question_text__ = OOBTree()
        super(Question, self).__init__(data = data, **kwargs)

    def get_original_title(self, default = u""):
        return self._field_storage.get('title', default)

    def get_title(self, lang=None, context=None, default=u"", **kwargs):
        """ Note that get title has some fault tolerant behaviour so we don't have to
            use a full test setup to investigate this model.
        """
        #Make sure we have a valid context
        request = get_current_request()
        if not context:
            context = getattr(request, 'context', None)
        #Check if there is a variant for the question for lang
        if not lang and context is not None:
            trans_util = request.registry.getUtility(IQuestionTranslations)
            lang = trans_util.default_locale_name
        #Is there a local question with that lang?
        organisation = find_interface(context, IOrganisation)
        if organisation:
            variant = organisation.get_variant(self.__name__, lang)
            if variant:
                return variant
        #Check for local language
        question_texts = self.get_question_text()
        if lang in question_texts:
            return question_texts[lang]
        #Fallback, english title
        return self._field_storage.get('title', default)

    @property
    def is_variant(self, lang=None, context=None, default=u"", **kwargs):
        """ Is the title returned by get_title a local variant, True/False?
        """
        #Make sure we have a valid context
        request = get_current_request()
        if not context:
            context = getattr(request, 'context', None)
        #Check if there is a variant for the question for lang
        if not lang and context is not None:
            trans_util = request.registry.getUtility(IQuestionTranslations)
            lang = trans_util.default_locale_name
        #Is there a local question with that lang?
        organisation = find_interface(context, IOrganisation)
        if organisation and self.__name__ in organisation.variants:
            for variant in organisation.variants[self.__name__].values():
                if variant:
                    return True
        return False
                                                        
    def _get_tags(self, **kw):
        return self._field_storage.get('tags', frozenset())
    def _set_tags(self, value, **kw):
        value = frozenset(value)
        self._field_storage['tags'] = value
    tags = property(_get_tags, _set_tags)

    def get_question_text(self, **kw):
        return self.__question_text__

    def set_question_text(self, value, **kw):
        """ This is only for the translations of the question, since the title is the base language.
            value here should be a dict with country codes as keys and questions as values.
            Any empty value should be removed before saving.
        """
        for (k, v) in value.items():
            if not v.strip():
                del value[k]
        self.__question_text__ = value

    def set_question_text_lang(self, value, lang):
        """ Set translation for specific language
        """
        question_text = self.get_question_text()
        if value:
            question_text[lang] = value
        else:
            if lang in question_text:
                del question_text[lang]
        self.__question_text__ = question_text

    def get_question_type(self):
        """ Return a dict with country codes as key and question translations as value. """
        #b/c compat
        return self.get_field_value('question_type', default = "")

    def set_question_type(self, value):
        #b/c compat
        self.set_field_value('question_type', value)

    def question_schema_node(self, name, lang=None, context=None):
        #If the correct question type isn't set, this might raise a ComponentLookupError
        node_util = getUtility(IQuestionNode, name=self.get_question_type())
        return node_util.node(name, title=self.get_title(lang, context=context))

    def render_result(self, request, data):
        if not data:
            return _(u"(Nothing)")
        node_util = getUtility(IQuestionNode, name=self.get_question_type())
        return node_util.render_result(request, data)

    def csv_export(self, data):
        if not data:
            return ()
        node_util = getUtility(IQuestionNode, name=self.get_question_type())
        return node_util.csv_export(data)
