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
def deferred_survey_title(node, kw):
    title = kw.get('survey_title', None)
    if title is None:
        raise ValueError("survey_title must be part of schema binding.")
    return title
    
@colander.deferred
def deferred_survey_section_title(node, kw):
    title = kw.get('survey_section_title', None)
    if title is None:
        raise ValueError("survey_section_title must be part of schema binding.")
    return title

class SurveySectionSchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    question_type = colander.SchemaNode(colander.String(),
                                        widget=deferred_question_type_widget,)

class SectionsSequenceSchema(colander.SequenceSchema):
    section = SurveySectionSchema()

class AddSurveySchema(colander.Schema):
    title = colander.SchemaNode(colander.String(),)
    sections = SectionsSequenceSchema(title=_(u"Add sections"),)



CONTENT_SCHEMAS = {'AddQuestion':AddQuestionSchema,
                   'EditQuestion':EditQuestionSchema,
                   'AddSurvey':AddSurveySchema,}


#Question schemas

@colander.deferred
def deferred_question_title(node, kw):
    title = kw.get('question_title', None)
    if title is None:
        raise ValueError("question_title must be part of schema binding.")
    return title


class FreeTextQuestionSchema(colander.Schema):
    answer = colander.SchemaNode(colander.String(),
                                 missing=u'',
                                 title=deferred_question_title)


importance_choices = \
    (('1', _(u'1 - Not important')),
     ('2', u'2'),
     ('3', u'3'),
     ('4', u'4'),
     ('5', u'5'),
     ('6', u'6'),
     ('7', _(u'7 - Very important')),)


class ImportanceScaleQuestionSchema(colander.Schema):
    answer = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in importance_choices]),
                widget=deform.widget.RadioChoiceWidget(values=importance_choices),
                title=deferred_question_title,)


frequency_scale = \
    (('never', _(u'(almost) never')),
     ('sometimes', _(u'sometimes yes / sometimes no')),
     ('always', _(u'(almost) always')),
     ('n_a', _(u'not applicable (n.a.)')),)


class FrequencyScaleQuestionSchema(colander.Schema):
    answer = colander.SchemaNode(
                colander.String(),
                validator=colander.OneOf([x[0] for x in frequency_scale]),
                widget=deform.widget.RadioChoiceWidget(values=frequency_scale),
                title=deferred_question_title,)



QUESTION_SCHEMAS = {'FreeTextQuestion': FreeTextQuestionSchema,
                    'ImportanceScaleQuestion': ImportanceScaleQuestionSchema,
                    'FrequencyScaleQuestion': FrequencyScaleQuestionSchema,}
