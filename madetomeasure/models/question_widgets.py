import deform
from zope.component import adapts
from zope.interface import implements

from madetomeasure.interfaces import IChoiceQuestionType
from madetomeasure.interfaces import ITextQuestionType
from madetomeasure.interfaces import IQuestionWidget


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

    def __call__(self):
        return deform.widget.TextInputWidget()


class RadioWidget(BaseQuestionWidget):
    name = u'radio_widget'
    title = u"Radio choice"
    adapts(IChoiceQuestionType)

    def __call__(self):
        choices = [(name, choice.title) for (name, choice) in self.context.items()]
        return deform.widget.RadioChoiceWidget(values=choices)


def includeme(config):
    config.registry.registerAdapter(TextWidget, name = TextWidget.name)
    config.registry.registerAdapter(RadioWidget, name = RadioWidget.name)