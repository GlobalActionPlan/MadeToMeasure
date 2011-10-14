import colander
import deform
from zope.interface import implements
from BTrees.OOBTree import OOBTree
from pyramid.renderers import render

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionNode


importance_choices = \
    (('1', _(u'1 - Not important')),
     ('2', u'2'),
     ('3', u'3'),
     ('4', u'4'),
     ('5', u'5'),
     ('6', u'6'),
     ('7', _(u'7 - Very important')),)
importance_choices_widget = deform.widget.RadioChoiceWidget(values=importance_choices)


frequency_scale = \
    (('never', _(u'(almost) never')),
     ('sometimes', _(u'sometimes yes / sometimes no')),
     ('always', _(u'(almost) always')),
     ('n_a', _(u'not applicable (n.a.)')),)
frequency_scale_choices_widget = deform.widget.RadioChoiceWidget(values=frequency_scale)


yes_no_choices = (('yes', _(u"Yes")), ('no', _(u"No")) )
yes_no_choices_widget = deform.widget.RadioChoiceWidget(values=yes_no_choices)


yes_no_maybe_choices = (('yes', _(u"Yes")), ('no', _(u"No")), ('maybe', _(u"Maybe")) )
yes_no_maybe_choices_widget = deform.widget.RadioChoiceWidget(values=yes_no_maybe_choices)


gender_choices = (('female', _(u"Female")), ('male', _(u"Female")) )
gender_choices_widget = deform.widget.RadioChoiceWidget(values=gender_choices)


text_area_widget = deform.widget.TextAreaWidget(cols=60, rows=10)
string_widget = deform.widget.TextInputWidget(size = 20)

class BasicQuestionNode(object):
    """ A question node that simply displays all of its results. """
    implements(IQuestionNode)
    
    def __init__(self, type_title, widget, **kwargs):
        """ Create object.
            Note that type_title is not the colander.SchemaNode's title

            You can pass along keyword arguments that will be accepted
            by the SchemaNode class.
            Tip: title, description, missing and validator are common.
        """
        self.type_title = type_title
        self.widget = widget
        self.default_kwargs = kwargs
    
    def node(self, name, **kwargs):
        """ Return a schema node.
        """
        kw = {}
        kw.update(self.default_kwargs)
        kw.update(kwargs)
        return colander.SchemaNode(colander.String(),
                                   name=name,
                                   widget=self.widget,
                                   **kw)

    def __repr__(self): # pragma: no cover
        return "<%s '%s'>" % (self.__class__.__module__, self.type_title)

    def count_occurences(self, data):
        results = OOBTree()
        for item in data:
            if item not in results:
                results[item] = 1
            else:
                results[item]+=1
        return results

    def render_result(self, request, data):
        response = {'data':data,}
        return render('../views/templates/results/basic.pt', response, request=request)
        
    def csv_header(self):
        return [self.type_title.encode('utf-8')]
        
    def csv_export(self, data):
        response = []
        for reply in data:
            response.append(['', reply.encode('utf-8')])
        
        return response


class ChoiceQuestionNode(BasicQuestionNode):
    """ Single choice type of question. """
    
    def choice_values(self):
        """ Return dict of possible choices with choice id as key,
            and rendered title as value.
        """
        choices = {}
        for (id, title) in self.widget.values:
            choices[id] = title
        return choices
    
    def render_result(self, request, data):
        response = {}
        response['occurences'] = self.count_occurences(data)
        response['choices'] = self.choice_values()
        return render('../views/templates/results/choice.pt', response, request=request)
        
    def csv_header(self):
        response = []
        response.append(self.type_title.encode('utf-8'))
        response.append(_(u"Total"))
        for choice in self.widget.values:
            response.append(choice[1].encode('utf-8'))
        
        return response
        
    def csv_export(self, data):
        response = []
        choices = self.choice_values()
        occurences = []
        if data:
            occurences = self.count_occurences(data)
        result = []
        for choice in choices:
            if choice in occurences:
                result.append(occurences[choice])
            else:
                result.append(0)
        response.append(sum(result))
        response.extend(result)

        return [response]


def includeme(config):
    #FIXME: Make utility registratio configurable?
    
    free_text = BasicQuestionNode(_(u"Free text question"), text_area_widget, missing=u"")
    config.registry.registerUtility(free_text, IQuestionNode, 'free_text')

    string_text = BasicQuestionNode(_(u"Small text input question"), string_widget, missing=u"")
    config.registry.registerUtility(string_text, IQuestionNode, 'string_text')

    importance_scale = ChoiceQuestionNode(_(u"Importance scale question"), importance_choices_widget)
    config.registry.registerUtility(importance_scale, IQuestionNode, 'importance_scale')

    frequency_scale = ChoiceQuestionNode(_(u"Frequency scale question"), frequency_scale_choices_widget)
    config.registry.registerUtility(frequency_scale, IQuestionNode, 'frequency_scale')
    
    yes_no = ChoiceQuestionNode(_(u"Yes / No question"), yes_no_choices_widget)
    config.registry.registerUtility(yes_no, IQuestionNode, 'yes_no')

    yes_no_maybe = ChoiceQuestionNode(_(u"Yes / No / Maybe question"), yes_no_maybe_choices_widget)
    config.registry.registerUtility(yes_no_maybe, IQuestionNode, 'yes_no_maybe')

    gender = ChoiceQuestionNode(_(u"Gender question"), gender_choices_widget)
    config.registry.registerUtility(gender, IQuestionNode, 'gender')
