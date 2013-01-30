import colander
import deform
from zope.component import getUtilitiesFor
from pyramid.traversal import find_interface

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionNode
from madetomeasure.interfaces import IQuestions

def question_text_node():
    return colander.Schema(title=_(u"Question translations"),
                           description=_(u"For each language")) #Send this to add_translations_schema

@colander.deferred
def deferred_tags_widget(node, kw):
    context = kw['context']
    questions = find_interface(context, IQuestions)
    tags = set()
    [tags.update(x.tags) for x in questions.values()]
    return deform.widget.AutocompleteInputWidget(
                title = _(u"Tags"),
                size=60,
                values = tuple(tags),
            )


def adjust_tags(value):
    value = value.lower()
    value = value.replace(" ", "_")
    return value


class TagsSequence(colander.SequenceSchema):
    text = colander.SchemaNode(
        colander.String(),
        preparer = adjust_tags,
        validator=colander.Length(max=100),
        widget=deferred_tags_widget,
        description='Enter some text (Hint: try "b" or "t")')


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
