import colander
import deform
from zope.component import getUtilitiesFor

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionNode


def question_text_node():
    return colander.Schema(title=_("Question translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema


@colander.deferred
def deferred_question_type_widget(node, kw):
    choices = []
    for (name, util) in getUtilitiesFor(IQuestionNode):
        choices.append((name, util.type_title))
    return deform.widget.RadioChoiceWidget(values=choices)

@colander.deferred
def deferred_context_title(node, kw):
    return kw.get('title')


class AddQuestionSchema(colander.Schema):
    question_type = colander.SchemaNode(colander.String(),
                                        title = _(u"Question type"),
                                        widget=deferred_question_type_widget,)
    title = colander.SchemaNode(colander.String(),
                                title=_(u"Initial question text, should be in English"),
                                description=_(u"Note that you can't change the text later, only its translations"),)
    question_text = question_text_node()



class EditQuestionSchema(colander.Schema):
    question_text = question_text_node()



class TranslateQuestionSchema(colander.Schema):
    question_text = question_text_node()
