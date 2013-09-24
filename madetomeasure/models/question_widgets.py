import deform
from zope.component import adapts
from zope.interface import implements

from madetomeasure.interfaces import IChoiceQuestionType
from madetomeasure.interfaces import ITextQuestionType
from madetomeasure.interfaces import IQuestionWidget
from madetomeasure import MadeToMeasureTSF as _


class BaseQuestionWidget(object):
    implements(IQuestionWidget)
    name = u''
    title = u''
    valid_for = ()

    def __init__(self, context):
        self.context = context


class TextWidget(BaseQuestionWidget):
    name = u'text_widget'
    title = u"Text string"
    adapts(ITextQuestionType)

    def __call__(self, **kw):
        return deform.widget.TextInputWidget()


class TextAreaWidget(BaseQuestionWidget):
    name = u'text_area_widget'
    title = u"Text area"
    adapts(ITextQuestionType)

    def __call__(self, **kw):
        return deform.widget.TextAreaWidget(cols = 60, rows = 10)


class RadioWidget(BaseQuestionWidget):
    name = u'radio_widget'
    title = u"Radio choice"
    adapts(IChoiceQuestionType)

    def __call__(self, **kw):
        lang = kw.get('lang', None)
        choices = [(name, choice.get_title(lang = lang)) for (name, choice) in self.context.items()]
        return deform.widget.RadioChoiceWidget(values=choices)


class DropdownWidget(BaseQuestionWidget):
    name = u'dropdown_widget'
    title = u"Dropdown choice"
    adapts(IChoiceQuestionType)

    def __call__(self, **kw):
        lang = kw.get('lang', None)
        choices = [('', _(u"<Select>"))]
        choices.extend([(name, choice.get_title(lang = lang)) for (name, choice) in self.context.items()])
        return deform.widget.SelectWidget(values=choices)


def includeme(config):
    config.registry.registerAdapter(TextWidget, name = TextWidget.name)
    config.registry.registerAdapter(TextAreaWidget, name = TextAreaWidget.name)
    config.registry.registerAdapter(RadioWidget, name = RadioWidget.name)
    config.registry.registerAdapter(DropdownWidget, name = DropdownWidget.name)
