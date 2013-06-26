from copy import copy

import colander
import deform
from zope.component import adapts
from zope.interface import implements
from zope.component import getAdapter
from zope.component import getUtility
from BTrees.OOBTree import OOBTree
from pyramid.renderers import render
from betahaus.pyracont.decorators import content_factory
from betahaus.pyracont import BaseFolder
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import DENY_ALL

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure import security
from madetomeasure.interfaces import IChoice
from madetomeasure.interfaces import IQuestionNode
from madetomeasure.interfaces import IQuestionWidget
from madetomeasure.interfaces import IQuestionType
from madetomeasure.interfaces import IQuestionTypes
from madetomeasure.interfaces import ITextQuestionType
from madetomeasure.interfaces import IChoiceQuestionType
from madetomeasure.models.security_aware import SecurityAware


class QuestionTypes(BaseFolder, SecurityAware):
    implements(IQuestionTypes)
    content_type = 'QuestionTypes'
    display_name = _(u"Question types")
    title = display_name
    allowed_contexts = () #N/A
    
    __acl__ = [(Allow, security.ROLE_ADMIN, ALL_PERMISSIONS),
               DENY_ALL,
              ]


class BaseQuestionType(BaseFolder, SecurityAware):
    implements(IQuestionType)
    allowed_contexts = ('QuestionTypes',)
    default_kwargs = {}

    @property
    def widget(self):
        widget_name = self.get_field_value('input_widget', '')
        return getAdapter(self, IQuestionWidget, name = widget_name)

    def node(self, name, **kwargs):
        """ Return a schema node.
        """
        kw = copy(self.default_kwargs)
        kw['name'] = name
        kw['widget'] = self.widget() #FIXME:Request?
        kw.update(kwargs)
        return colander.SchemaNode(colander.String(), **kw)

    def count_occurences(self, data):
        results = OOBTree()
        for item in data:
            if item not in results:
                results[item] = 1
            else:
                results[item]+=1
        return results

    def __repr__(self): # pragma: no cover
        return "<%s '%s'>" % (self.__class__.__module__, self.title)

    def render_result(self, request, data):
        raise NotImplementedError()
        
    def csv_header(self):
        raise NotImplementedError()
        
    def csv_export(self, data):
        raise NotImplementedError()

@content_factory('TextQuestionType')
class TextQuestionType(BaseQuestionType):
    implements(ITextQuestionType)
    content_type = u'TextQuestionType'
    display_name = _(u"Text question")
    description = _(u"")

    def render_result(self, request, data):
        response = {'data':data,}
        return render('../views/templates/results/basic.pt', response, request=request)
        
    def csv_header(self):
        return [self.title]
        
    def csv_export(self, data):
        response = []
        for reply in data:
            response.append(['', reply.encode('utf-8')])
        return response


@content_factory('ChoiceQuestionType')
class ChoiceQuestionType(BaseQuestionType):
    implements(IChoiceQuestionType)
    content_type = 'ChoiceQuestionType'
    display_name = _(u"Choice question")
    description = _(u"")

    def choice_values(self):
        """ Return dict of possible choices with choice id as key,
            and rendered title as value.
        """
        choices = {}
        for (id, title) in self.widget().values:
            choices[id] = title
        return choices
    
    def render_result(self, request, data):
        response = {}
        response['occurences'] = self.count_occurences(data)
        response['choices'] = self.choice_values()
        return render('../views/templates/results/choice.pt', response, request=request)
        
    def csv_header(self):
        response = []
        response.append(self.title)
        response.append(_(u"Total"))
        for (id, title) in self.widget().values:
            response.append(title.encode('utf-8'))
        return response
        
    def csv_export(self, data):
        response = []
        occurences = []
        if data:
            occurences = self.count_occurences(data)
        result = []
        for (id, title) in self.widget().values:
            if id in occurences:
                result.append(occurences[id])
            else:
                result.append(0)
        response.append(sum(result))
        response.extend(result)
        return [response]


@content_factory('Choice')
class Choice(BaseFolder, SecurityAware):
    """Documentation found in interfaces/IChoice
    """
    implements(IChoice)
    content_type = u'Choice'
    display_name = _(u"Choice")
    description = _(u"")
    allowed_contexts = ('ChoiceQuestionType',)
    custom_mutators = {'title_translations': 'set_title_translations'}

    def get_title(self, lang=None):
        if not lang:
            # If no language specified fall-back to default locale.
            request = get_current_request()
            trans_util = request.registry.getUtility(IQuestionTranslations)
            lang = trans_util.default_locale_name
        #Check for local language
        translations = self.get_field_value('title_translations', {})
        return translations.get(lang, self.title)

    def set_title_translations(self, value, **kw):
        if 'title_translations' not in self.field_storage:
            self.field_storage['title_translations'] = OOBTree()
        self.field_storage['title_translations'].clear()
        self.field_storage['title_translations'].update(value)
