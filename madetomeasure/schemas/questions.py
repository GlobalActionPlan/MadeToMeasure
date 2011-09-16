import colander
import deform
from zope.component import getUtilitiesFor

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionNode


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
    title = colander.SchemaNode(colander.String(),
                                title=_(u"Initial question text"),
                                description=_(u"Normally in english - note that you can't change the text later, only its translations"),)
    question_type = colander.SchemaNode(colander.String(),
                                      widget=deferred_question_type_widget,)
    question_text = colander.Schema(title=_("Question translations"),
                                    description=_(u"For each country code")) #Send this to add_translations_schema


class EditQuestionSchema(colander.Schema):
    question_text = colander.Schema(title=_("Question translations"),
                                    description=_(u"For each country code")) #Send this to add_translations_schema

