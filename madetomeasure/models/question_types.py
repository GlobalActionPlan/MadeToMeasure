from copy import copy

import colander
import deform
from zope.interface import implements
from zope.component import queryAdapter
from BTrees.OOBTree import OOBTree
from pyramid.renderers import render
from betahaus.pyracont.decorators import content_factory
from betahaus.pyracont import BaseFolder
from pyramid.security import Allow
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import DENY_ALL
from pyramid.threadlocal import get_current_request
from pyramid.traversal import find_root

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure import security
from madetomeasure.interfaces import IChoice
from madetomeasure.interfaces import IQuestionWidget
from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure.interfaces import IQuestionType
from madetomeasure.interfaces import IQuestionTypes
from madetomeasure.interfaces import ITextQuestionType
from madetomeasure.interfaces import INumberQuestionType
from madetomeasure.interfaces import IChoiceQuestionType
from madetomeasure.interfaces import IMultiChoiceQuestionType
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
    """ See interfaces for docs """
    implements(IQuestionType)
    allowed_contexts = ('QuestionTypes',)
    uid_name = True
    go_to_after_add = u'edit'

    @property
    def widget(self):
        widget_name = self.get_field_value('input_widget', '')
        return queryAdapter(self, IQuestionWidget, name = widget_name)

    @property
    def default_kwargs(self):
        return self.get_field_value('default_kwargs', {})

    @default_kwargs.setter
    def default_kwargs(self, value):
        self.set_field_value('default_kwargs', dict(value))

    @property
    def description(self):
        return self.get_field_value('description', u'')

    def node(self, name, lang = None, **kwargs):
        kw = copy(self.default_kwargs)
        kw['name'] = name
        if self.widget:
            kw['widget'] = self.widget(lang = lang)
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
        response = {'data':data,}
        return render('../views/templates/results/basic.pt', response, request=request)

    def csv_header(self):
        return [self.title]

    def csv_export(self, data):
        response = []
        for reply in data:
            if isinstance(reply, basestring):
                response.append(['', reply.encode('utf-8')])
            else:
                response.append(['', reply])
        return response

    def check_safe_delete(self, request):
        root = find_root(self)
        results = root['questions'].questions_by_type(self.__name__)
        if not results:
            return True
        #FIXME: Only flash messages can handle html right now
        out = u"<br/><br/>"
        rurl = request.resource_url
        out += ",<br/>".join([u'<a href="%s">%s</a>' % (rurl(x), x.title) for x in results])
        request.session.flash(_(u"Can't delete this since it's used in: ${out}",
                                mapping = {'out': out}))
        return False


@content_factory('TextQuestionType')
class TextQuestionType(BaseQuestionType):
    implements(ITextQuestionType)
    content_type = u'TextQuestionType'
    display_name = _(u"Text question")
    schemas = {'add': 'AddQuestionTypeSchema', 'edit': 'EditTextQuestionSchema', 'delete': 'DeleteQuestionTypeSchema'}


@content_factory('NumberQuestionType')
class NumberQuestionType(BaseQuestionType):
    implements(INumberQuestionType)
    content_type = u'NumberQuestionType'
    display_name = _(u"Number question")
    schemas = {'add': 'AddQuestionTypeSchema', 'edit': 'EditNumberQuestionSchema', 'delete': 'DeleteQuestionTypeSchema'}

    def node(self, name, lang = None, **kwargs):
        kw = copy(self.default_kwargs)
        kw['name'] = name
        if self.widget:
            kw['widget'] = self.widget(lang = lang)
        kw.update(kwargs)
        return colander.SchemaNode(colander.Decimal(), **kw)


class BaseChoiceQuestionType(BaseQuestionType):

    def count_occurences(self, data):
        results = OOBTree()
        for item in data:
            if item not in results:
                results[item] = 1
            else:
                results[item]+=1
        return results

    def choice_values(self, lang = None):
        choices = {}
        for (id, title) in self.widget(lang = lang).values:
            choices[id] = title
        return choices

    def render_result(self, request, data):
        response = {}
        response['occurences'] = self.count_occurences(data)
        response['choices'] = self.choice_values(lang = request.cookies.get('_LOCALE_', None))
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


@content_factory('ChoiceQuestionType')
class ChoiceQuestionType(BaseChoiceQuestionType):
    implements(IChoiceQuestionType)
    content_type = 'ChoiceQuestionType'
    display_name = _(u"Choice question")
    schemas = {'add': 'AddQuestionTypeSchema', 'edit': 'EditChoiceQuestionSchema', 'delete': 'DeleteQuestionTypeSchema'}

    def node(self, name, lang = None, **kwargs):
        kw = copy(self.default_kwargs)
        kw['name'] = name
        if self.widget:
            kw['widget'] = self.widget(lang = lang)
        kw.update(kwargs)
        return colander.SchemaNode(colander.String(), **kw)


@content_factory('MultiChoiceQuestionType')
class MultiChoiceQuestionType(BaseChoiceQuestionType):
    implements(IMultiChoiceQuestionType)
    content_type = 'MultiChoiceQuestionType'
    display_name = _(u"Multiple choice question")
    schemas = {'add': 'AddQuestionTypeSchema', 'edit': 'EditMultipleChoiceQuestionSchema', 'delete': 'DeleteQuestionTypeSchema'}

    def node(self, name, lang = None, **kwargs):
        kw = copy(self.default_kwargs)
        kw['name'] = name
        if self.widget:
            kw['widget'] = self.widget(lang = lang)
        kw.update(kwargs)
        return colander.SchemaNode(deform.Set(allow_empty=True), **kw)

    def count_occurences(self, data):
        results = OOBTree()
        for item in data:
            for subitem in item:
                if subitem not in results:
                    results[subitem] = 1
                else:
                    results[subitem] += 1
        return results


@content_factory('Choice')
class Choice(BaseFolder, SecurityAware):
    """Documentation found in interfaces/IChoice
    """
    implements(IChoice)
    content_type = u'Choice'
    display_name = _(u"Choice")
    description = _(u"")
    allowed_contexts = ('ChoiceQuestionType', 'MultiChoiceQuestionType')
    custom_mutators = {'title_translations': 'set_title_translations'}
    schemas = {'add': 'ChoiceSchema', 'edit': 'ChoiceSchema',}
    uid_name = True

    def get_title(self, lang=None):
        if not lang:
            # If no language specified fall-back to default locale.
            request = get_current_request()
            trans_util = request.registry.getUtility(IQuestionTranslations)
            lang = trans_util.default_locale_name
        #Check for local language
        translations = self.get_field_value('title_translations', {})
        tr_title = translations.get(lang, None)
        return tr_title and tr_title or self.title

    def set_title_translations(self, value, **kw):
        if 'title_translations' not in self.field_storage:
            self.field_storage['title_translations'] = OOBTree()
        self.field_storage['title_translations'].clear()
        self.field_storage['title_translations'].update(value)
