import colander
import deform

from madetomeasure import MadeToMeasureTSF as _

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


