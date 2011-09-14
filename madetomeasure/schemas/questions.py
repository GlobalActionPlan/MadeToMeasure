import colander
import deform
from zope.component import getUtilitiesFor

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionNodeFactory


@colander.deferred
def deferred_question_type_widget(node, kw):
    choices = []
    for (name, util) in getUtilitiesFor(IQuestionNodeFactory):
        choices.append((name, util.type_title))
    return deform.widget.RadioChoiceWidget(values=choices)

@colander.deferred
def deferred_context_title(node, kw):
    return kw.get('title')

@colander.deferred
def deferred_lang_widget(node, kw):
    choices = (('sv', 'Svenska'),
               )
    return deform.widget.SelectWidget(values=choices)


class AddQuestionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String())
    question_type = colander.SchemaNode(colander.String(),
                                      widget=deferred_question_type_widget,)


class LangAndTextSchema(colander.Schema):
    lang = colander.SchemaNode(colander.String(),
                               widget=deferred_lang_widget,)
    text = colander.SchemaNode(colander.String())


class TranslationSequenceSchema(colander.SequenceSchema):
    translations = LangAndTextSchema()


class EditQuestionSchema(colander.Schema):
    question_text = TranslationSequenceSchema(title=_(u"Add translations"),)
