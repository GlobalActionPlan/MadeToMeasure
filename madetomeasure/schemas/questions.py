import colander
import deform
from zope.component import getUtilitiesFor

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.schemas.common import adjust_tags
from madetomeasure.schemas.common import deferred_tags_text_widget
from madetomeasure.schemas.common import deferred_tags_select_widget
from madetomeasure.interfaces import IQuestionNode


def question_text_node():
    return colander.Schema(title=_(u"Question translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema


class TagsSequence(colander.SequenceSchema):
    text = colander.SchemaNode(
        colander.String(),
        preparer = adjust_tags,
        validator=colander.All(colander.Length(max=100), colander.Regex('^\w*$', msg = _(u"Only letters and charracters a-z allowed"))),
        widget=deferred_tags_text_widget,
        description=_(u"Enter some text"))


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
                                widget=deform.widget.TextInputWidget(size=80),)
    question_text = question_text_node()
    tags = TagsSequence()


class EditQuestionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),
                                title=_(u"Initial question text, should be in English"),
                                widget=deform.widget.TextInputWidget(size=80),)
    question_text = question_text_node()
    tags = TagsSequence()


class TranslateQuestionSchema(colander.Schema):
    question_text = question_text_node()


class QuestionSearchSchema(colander.Schema):
    query = colander.SchemaNode(
        colander.String(),
        title = _(u"Free text")
    )
    tag =  colander.SchemaNode(
        colander.String(),
        widget=deferred_tags_select_widget,)
