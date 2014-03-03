from BTrees.OOBTree import OOBTree
from zope.interface import implements
from pyramid.traversal import find_interface
from pyramid.traversal import find_root
from betahaus.pyracont import BaseFolder
from betahaus.pyracont.decorators import content_factory
from pyramid.i18n import get_locale_name
from pyramid.threadlocal import get_current_request

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import ISurveySection
from madetomeasure.models.security_aware import SecurityAware


@content_factory('SurveySection')
class SurveySection(BaseFolder, SecurityAware):
    implements(ISurveySection)
    content_type = 'SurveySection'
    display_name = _(u"Survey Section")
    allowed_contexts = ('Survey',)
    custom_accessors = {}
    custom_mutators = {'order': 'set_order',
                       'heading_translations': 'set_heading_translations',
                       'description_translations': 'set_description_translations',
                       'question_ids': 'set_question_ids',}
    schemas = {'add': 'SurveySectionSchema', 'edit': 'SurveySectionSchema', 'delete': 'DeleteSurveySectionSchema'}


    def __init__(self, data=None, **kwargs):
        """  Init Survey section """
        super(SurveySection, self).__init__(data=data, **kwargs)
        self.__responses__ = OOBTree()

    def get_translated_title(self, lang = None, default=u""):
        """ This is a special version of title, since it might have translations.
            The regular setter works though, since the translations are stored in heading_translations.
        """
        if not lang:
            request = get_current_request()
            lang = get_locale_name(request)
        translations = self.get_field_value('heading_translations', {})
        if lang and lang in translations:
            return translations[lang]
        return self._field_storage.get('title', default)

    def get_translated_description(self, lang = None, default=u""):
        """ This is a special version of description, since it might have translations.
            The regular setter works though, since the translations are stored in description_translations.
        """
        if not lang:
            request = get_current_request()
            lang = get_locale_name(request)
        translations = self.get_field_value('description_translations', {})
        if lang and lang in translations:
            return translations[lang]
        return self._field_storage.get('description', default)

    @property
    def question_ids(self):
        return self.get_field_value('question_ids', ())

    def set_question_ids(self, value, **kw):
        value = tuple(value)
        self.field_storage['question_ids'] = value

    def get_question_type(self):
        #FIXME: Isn't this obsolete?
        return self.get_field_value('question_type', "")

    def set_heading_translations(self, value, key=None):
        """ This is only for the translations of the question, since the title is the base language.
            value here should be a dict with country codes as keys and questions as values.
            Any empty value should be removed before saving.
        """
        #b/c compat + clean input value
        for (k, v) in value.items():
            if not v.strip():
                del value[k]
        self.field_storage['heading_translations'] = value

    def set_description_translations(self, value, key=None):
        """ Set description translations. """
        for (k, v) in value.items():
            if not v.strip():
                del value[k]
        self.field_storage['description_translations'] = value

    def append_questions_to_schema(self, schema, request):
        """ Append all questions to a schema. """
        lang = None
        if '_LOCALE_' in request.cookies:
            lang = request.cookies['_LOCALE_']
        for id in self.question_ids:
            question = self.question_object_from_id(id)
            schema.add(question.question_schema_node(id, lang=lang, context=self))

    @property
    def responses(self):
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
        org = find_interface(self, IOrganisation)
        if id in org['questions']:
            return org['questions'][id]
        root = find_root(self)
        return root['questions'].get(id)

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
