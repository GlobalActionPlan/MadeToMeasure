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


importance_text_choices = \
    (('very_important', _(u"very important")),
     ('fairly_important', _(u"fairly important")),
     ('not_very_important', _(u"not very important")),
     ('unimportant', _(u"unimportant")),
     )
importance_text_choices_widget = deform.widget.RadioChoiceWidget(values=importance_text_choices)


agree_text_choices = \
    (('fully_agree', _(u"fully agree")),
     ('somewhat_agree', _(u"somewhat agree")),
     ('somewhat_disagree', _(u"somewhat disagree")),
     ('disagree', _(u"disagree")),
     )
agree_text_choices_widget = deform.widget.RadioChoiceWidget(values=agree_text_choices)


frequency_scale = \
    (('never', _(u'(almost) never')),
     ('lesshalf', _(u'less than half the time')),
     ('halv', _(u'around half the time')),
     ('morehalf', _(u'more than half')),
     ('always', _(u'(almost) always')),
     ('n_a', _(u'N/A')),)
frequency_scale_choices_widget = deform.widget.RadioChoiceWidget(values=frequency_scale)


yes_no_choices = (('yes', _(u"Yes")), ('no', _(u"No")) )
yes_no_choices_widget = deform.widget.RadioChoiceWidget(values=yes_no_choices)


yes_maybe_no_choices = (('yes', _(u"Yes")), ('maybe', _(u"Maybe")), ('no', _(u"No")), )
yes_maybe_no_choices_widget = deform.widget.RadioChoiceWidget(values=yes_maybe_no_choices)


gender_choices = (('female', _(u"Female")), ('male', _(u"Male")) )
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
        choices = self.choice_values()
        for choice in choices:
            response.append(choices[choice].encode('utf-8'))
        
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
    #FIXME: Make utility registration configurable?
    
    free_text = BasicQuestionNode(_(u"Free text question"), text_area_widget, missing=u"")
    config.registry.registerUtility(free_text, IQuestionNode, 'free_text')

    string_text = BasicQuestionNode(_(u"Small text input question"), string_widget, missing=u"")
    config.registry.registerUtility(string_text, IQuestionNode, 'string_text')

    importance_scale = ChoiceQuestionNode(_(u"Importance scale question 1-7"), importance_choices_widget)
    config.registry.registerUtility(importance_scale, IQuestionNode, 'importance_scale')

    importance_text_scale = ChoiceQuestionNode(_(u"Importance text question"), importance_text_choices_widget)
    config.registry.registerUtility(importance_text_scale, IQuestionNode, 'importance_text_scale')

    agree_text_choices = ChoiceQuestionNode(_(u"Agree text question"), agree_text_choices_widget)
    config.registry.registerUtility(agree_text_choices, IQuestionNode, 'agree_text_choices')

    frequency_scale = ChoiceQuestionNode(_(u"Frequency scale question"), frequency_scale_choices_widget)
    config.registry.registerUtility(frequency_scale, IQuestionNode, 'frequency_scale')

    yes_no = ChoiceQuestionNode(_(u"Yes / No question"), yes_no_choices_widget)
    config.registry.registerUtility(yes_no, IQuestionNode, 'yes_no')

    yes_maybe_no = ChoiceQuestionNode(_(u"Yes / Maybe question / No"), yes_maybe_no_choices_widget)
    config.registry.registerUtility(yes_maybe_no, IQuestionNode, 'yes_maybe_no')

    gender = ChoiceQuestionNode(_(u"Gender question"), gender_choices_widget)
    config.registry.registerUtility(gender, IQuestionNode, 'gender')
