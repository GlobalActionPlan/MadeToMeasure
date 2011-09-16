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


text_area_widget = deform.widget.TextAreaWidget(cols=60, rows=10)

class BasicQuestionNode(object):
    """ A question node that simply displays all of its results. """
    implements(IQuestionNode)
    
    def __init__(self, type_title, widget):
        """ Create object.
            Note that type_title is not the colander.SchemaNode's title
        """
        self.type_title = type_title
        self.widget = widget
    
    def node(self, name, **kw):
        """ Return a schema node.
            You can pass along keyword arguments that will be accepted
            by the SchemaNode class.
            Tip: We use title and validator
        """
        return colander.SchemaNode(colander.String(),
                                   name=name,
                                   widget=self.widget,
                                   **kw)

    def __repr__(self):
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


def includeme(config):
    #FIXME: Make utility registratio configurable?
    
    free_text = BasicQuestionNode(_(u"Free text question"), text_area_widget)
    config.registry.registerUtility(free_text, IQuestionNode, 'free_text')

    importance_scale = ChoiceQuestionNode(_(u"Importance scale question"), importance_choices_widget)
    config.registry.registerUtility(importance_scale, IQuestionNode, 'importance_scale')

    frequency_scale = ChoiceQuestionNode(_(u"Frequency scale question"), frequency_scale_choices_widget)
    config.registry.registerUtility(frequency_scale, IQuestionNode, 'frequency_scale')

