import colander
import deform
from zope.interface import implements

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionNodeFactory

#FIXME: Move to models?


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

class StringQuestionNode(object):
    
    def __init__(self, type_title, widget):
        """ Create object.
            Note that type_title is not the colander.SchemaNode's title
        """
        self.type_title = type_title
        self.widget = widget
    
    def __call__(self, name, **kw):
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
        return "<StringQuestionNode '%s'>" % self.type_title




def register_question_node_utilities(config):
    #FIXME: Make utility registratio configurable?
    
    free_text = StringQuestionNode(_(u"Free text question"), text_area_widget)
    config.registry.registerUtility(free_text, IQuestionNodeFactory, 'free_text')

    importance_scale = StringQuestionNode(_(u"Importance scale question"), importance_choices_widget)
    config.registry.registerUtility(importance_scale, IQuestionNodeFactory, 'importance_scale')

    frequency_scale = StringQuestionNode(_(u"Frequency scale question"), frequency_scale_choices_widget)
    config.registry.registerUtility(frequency_scale, IQuestionNodeFactory, 'frequency_scale')

