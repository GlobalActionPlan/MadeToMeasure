from BTrees.OOBTree import OOBTree
from zope.interface import implements
from pyramid.traversal import find_interface
from pyramid.traversal import find_root
from betahaus.pyracont import BaseFolder

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import ISurveySection
from madetomeasure.models.app import select_language
from madetomeasure.models.security_aware import SecurityAware


class SurveySection(BaseFolder, SecurityAware):
    implements(ISurveySection)
    content_type = 'SurveySection'
    display_name = _(u"Survey Section")
    allowed_contexts = ('Survey',)
    custom_accessors = {'title': 'get_title'}
    custom_mutators = {'order': 'set_order',
                       'heading_translations': 'set_heading_translations'}

    def __init__(self, data=None, **kwargs):
        """  Init Survey section """
        super(SurveySection, self).__init__(data=data, **kwargs)
        self.__responses__ = OOBTree()

    def get_title(self, key=None, default=u""):
        """ This is a special version of get title, since it might have translations.
            The regular setter works though, since the translations are stored in heading_translations.
        """
        #FIXME: Mame this a separate method, it does too compaired to regular title
        try:
            lang = select_language(self)
        except ValueError:
            lang = 'en'
        translations = self.get_field_value('heading_translations', {})
        if lang and lang in translations:
            return translations[lang]
        
        #FIXME: betahaus.pyracont is missing override option for custom getters
        return self._field_storage.get('title', default)
    
    @property
    def question_ids(self):
        uids = set()
        for v in self.get_structured_question_ids().values():
            uids.update(v)
        
        order = self.get_order()
        extra_uids = []
        for v in uids:
            if not v in order:
                extra_uids.append(v)
        
        if extra_uids:
            order = list(order)
            order.extend(extra_uids)
            order = tuple(order)
        return order
        
    def get_order(self):
        #b/c compat
        return self.get_field_value('order', ())
            
    def set_order(self, value, key=None):
        #b/c compat
        uids = set()
        for v in self.get_structured_question_ids().values():
            uids.update(v)
            
        order = []
        for v in value:
            if v in uids:
                order.append(v)
        
        order = tuple(order)
        self.set_field_value('order', order, override=True)

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
        self.set_field_value('heading_translations', value, override=True)

    def get_structured_question_ids(self):
        #b/c compat
        return self.get_field_value('structured_question_ids', default={})

    def append_questions_to_schema(self, schema, request):
        """ Append all questions to a schema. """
        
        lang = None
        if 'lang' in request.session:
            lang = request.session['lang']
 
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
