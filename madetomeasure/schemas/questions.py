import colander
import deform

from madetomeasure import MadeToMeasureTSF as _


@colander.deferred
def deferred_question_type_widget(node, kw):
    choices = [(x, x) for x in QUESTION_SCHEMAS.keys()]
    return deform.widget.RadioChoiceWidget(values=choices)

@colander.deferred
def deferred_context_title(node, kw):
    return kw.get('title')

@colander.deferred
def deferred_lang_widget(node, kw):
    choices = (('sv', 'Svenska'),
               ('en', 'English'),
               )
    return deform.widget.SelectWidget(values=choices)


class AddQuestionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String())
    question_type_schema = colander.SchemaNode(colander.String(),
                                      widget=deferred_question_type_widget,)


class LangAndTextSchema(colander.Schema):
    lang = colander.SchemaNode(colander.String(),
                               widget=deferred_lang_widget,)
    text = colander.SchemaNode(colander.String())


class TranslationSequenceSchema(colander.SequenceSchema):
    translations = LangAndTextSchema()


class EditQuestionSchema(colander.Schema):
    question_text = TranslationSequenceSchema(title=_(u"Add translations"),)
