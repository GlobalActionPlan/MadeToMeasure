import deform
from zope.component import adapts
from zope.interface import implements

from madetomeasure.interfaces import IChoiceQuestionType
from madetomeasure.interfaces import IMultiChoiceQuestionType
from madetomeasure.interfaces import ITextQuestionType
from madetomeasure.interfaces import IIntegerQuestionType
from madetomeasure.interfaces import INumberQuestionType
from madetomeasure.interfaces import IQuestionWidget
from madetomeasure import MadeToMeasureTSF as _


class BaseQuestionWidget(object):
    implements(IQuestionWidget)
    name = u''
    title = u''

    def __init__(self, context):
        self.context = context


class TextWidget(BaseQuestionWidget):
    name = u'text_widget'
    title = _(u"Text string")
    adapts(ITextQuestionType)

    def __call__(self, **kw):
        return deform.widget.TextInputWidget()


class IntegerWidget(BaseQuestionWidget):
    #DEPRECATED - WILL BE REMOVED
    name = u'integer_widget'
    title = _(u"Integer number field")
    adapts(IIntegerQuestionType)

    def __call__(self, **kw):
        return deform.widget.TextInputWidget()

class NumberWidget(BaseQuestionWidget):
    name = u'number_widget'
    title = _(u"Number field")
    adapts(INumberQuestionType)

    def __call__(self, **kw):
        return deform.widget.TextInputWidget()


class TextAreaWidget(BaseQuestionWidget):
    name = u'text_area_widget'
    title = _(u"Text area")
    adapts(ITextQuestionType)

    def __call__(self, **kw):
        return deform.widget.TextAreaWidget(cols = 60, rows = 10)


class RadioWidget(BaseQuestionWidget):
    name = u'radio_widget'
    title = _(u"Radio choice")
    adapts(IChoiceQuestionType)

    def __call__(self, **kw):
        lang = kw.get('lang', None)
        choices = [(name, choice.get_title(lang = lang)) for (name, choice) in self.context.items()]
        return deform.widget.RadioChoiceWidget(values=choices)


class DropdownWidget(BaseQuestionWidget):
    name = u'dropdown_widget'
    title = _(u"Dropdown choice")
    adapts(IChoiceQuestionType)

    def __call__(self, **kw):
        lang = kw.get('lang', None)
        choices = [('', _(u"<Select>"))]
        choices.extend([(name, choice.get_title(lang = lang)) for (name, choice) in self.context.items()])
        return deform.widget.SelectWidget(values=choices)


class CheckboxWidget(BaseQuestionWidget):
    name = u"checkbox_widget"
    title = _(u"Checkbox multichoice")
    adapts(IMultiChoiceQuestionType)

    def __call__(self, **kw):
        lang = kw.get('lang', None)
        choices = []
        choices.extend([(name, choice.get_title(lang = lang)) for (name, choice) in self.context.items()])
        return deform.widget.CheckboxChoiceWidget(values=choices)


def includeme(config):
    config.registry.registerAdapter(TextWidget, name = TextWidget.name)
    config.registry.registerAdapter(IntegerWidget, name = IntegerWidget.name)
    config.registry.registerAdapter(NumberWidget, name = NumberWidget.name)
    config.registry.registerAdapter(TextAreaWidget, name = TextAreaWidget.name)
    config.registry.registerAdapter(RadioWidget, name = RadioWidget.name)
    config.registry.registerAdapter(DropdownWidget, name = DropdownWidget.name)
    config.registry.registerAdapter(CheckboxWidget, name = CheckboxWidget.name)
