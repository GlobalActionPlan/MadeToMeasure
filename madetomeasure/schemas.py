import colander
import deform

from madetomeasure import MadeToMeasureTSF as _


@colander.deferred
def deferred_question_type_widget(node, kw):
    choices = [(x, x) for x in QUESTION_SCHEMAS.keys()]
    return deform.widget.SelectWidget(values=choices)

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


CONTENT_SCHEMAS = {'AddQuestion':AddQuestionSchema,
                   'EditQuestion':EditQuestionSchema,}


@colander.deferred
def deferred_came_from(node, kw):
    return kw.get('came_from', u'')


class LoginSchema(colander.Schema):
    userid = colander.SchemaNode(colander.String(),
                                 title=_(u"UserID"))
    password = colander.SchemaNode(colander.String(),
                                   title=_('Password'),
                                   widget=deform.widget.PasswordWidget(size=20),)
    came_from = colander.SchemaNode(colander.String(),
                                    widget = deform.widget.HiddenWidget(),
                                    missing='',
                                    default=deferred_came_from,)


@colander.deferred
def deferred_question_title(node, kw):
    title = kw.get('question_title', None)
    if title is None:
        raise ValueError("question_title must be part of schema binding.")
    return title

class FreeTextQuestionSchema(colander.Schema):
    text = colander.SchemaNode(colander.String(),
                               missing=u'',
                               title=deferred_question_title)


QUESTION_SCHEMAS = {'FreeTextQuestion': FreeTextQuestionSchema}