import colander
import deform
from betahaus.pyracont.decorators import schema_factory

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionWidget


def title_node():
    return colander.SchemaNode(colander.String(),
                               title = _(u"Title"),
                               )

def description_node():
    return colander.SchemaNode(colander.String(),
                               title = _(u"Description"),
                               missing = u"",
                               )

def input_widget_node():
    return colander.SchemaNode(colander.String(),
                               title = _(u"Input widget"),
                               widget = deferred_input_widget,)


@colander.deferred
def deferred_input_widget(node, kw):
    values = []
    request = kw['request']
    context = kw['context']
    for (name, widget) in request.registry.getAdapters([context], IQuestionWidget):
        values.append((name, widget.title))
    return deform.widget.RadioChoiceWidget(values = values)


@schema_factory('AddQuestionTypeSchema', title = _(u"Add question type"))
class AddQuestionTypeSchema(colander.Schema):
    title = title_node()


@schema_factory('EditTextQuestionSchema')
class EditTextQuestionSchema(colander.Schema):
    title = title_node()
    description = description_node()
    input_widget = input_widget_node()


@schema_factory('EditChoiceQuestionSchema')
class EditChoiceQuestionSchema(colander.Schema):
    title = title_node()
    description = description_node()
    input_widget = input_widget_node()


@schema_factory('ChoiceSchema')
class ChoiceSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title = _(u"Base choice value - visible to users"),
                                )
    ignore_translations = colander.SchemaNode(colander.Bool(),
                                              title = _(u"Ignore translations"),
                                              description = _(u"If the title is numerical for instance, there's no reason to handle translations. Translations won't be stored if this is checked."))
