from operator import itemgetter

import colander
import deform
from pytz import common_timezones
from zope.component import getUtility
from pyramid.traversal import find_root
from pyramid.traversal import find_interface

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IQuestions


def time_zone_node():
    return colander.SchemaNode(
        colander.String(),
        title = _(u"Timezone"),
        description = _(u"Try start typing a timezone"),
        validator = colander.OneOf(common_timezones),
        widget = deform.widget.AutocompleteInputWidget(size=60,
                                                   values = list(common_timezones), #Conversion due to API change in pytz
                                                   min_length=1),
    )

def _get_langs(omit = ()):
    util = getUtility(IQuestionTranslations)
    sort = []
    for lang in util.available_languages:
        if lang not in omit:
            sort.append((lang, util.title_for_code_default(lang).lower()))
    sort = sorted(sort, key=itemgetter(1))
    choices = []
    for (lang, name) in sort:
        name = "%s - %s (%s)" % (util.title_for_code_default(lang), util.title_for_code(lang), lang)
        choices.append((lang, name))
    return choices

def adjust_tags(value):
    if not value:
        return value
    value = value.lower()
    value = value.replace(" ", "_")
    return value

@colander.deferred
def deferred_available_languages_widget(node, kw):
    return deform.widget.CheckboxChoiceWidget(values = _get_langs())

@colander.deferred
def deferred_translator_languages_widget(node, kw):
    return deform.widget.CheckboxChoiceWidget(values = _get_langs(omit = ('en',)))

@colander.deferred
def deferred_pick_language_widget(node, kw):
    return deform.widget.SelectWidget(values = _get_langs())


def _fetch_questions_for_tags(context):
    if IQuestions.providedBy(context):
        questions = context.values()
    else:
        questions = []
        questions.extend(find_root(context)['questions'].values())
        org = find_interface(context, IOrganisation)
        if org:
            questions.extend(org['questions'].values())
    return questions


@colander.deferred
def deferred_tags_text_widget(node, kw):
    context = kw['context']
    questions = _fetch_questions_for_tags(context)
    tags = set()
    [tags.update(x.tags) for x in questions]
    return deform.widget.AutocompleteInputWidget(
                title = _(u"Tags"),
                size=60,
                values = tuple(tags),
            )

@colander.deferred
def deferred_tags_select_widget(node, kw):
    """ Fetch all selectable tags. Context here probably be anything,
        but if it is a questions folder, only those tags should be fetched.
        Otherwise, if it's within an organisation, fetch those tags and apply the global tags.
    """
    context = kw['context']
    questions = _fetch_questions_for_tags(context)
    tags = {}
    for question in questions:
        for tag in question.tags:
            try:
                tags[tag] += 1
            except KeyError:
                tags[tag] = 1
    order = sorted(tags.keys())
    results = [(u'', _(u'<select>'))]
    for k in order:
        results.append((k, u"%s (%s)" % (k, tags[k])))
    return deform.widget.SelectWidget(
                title = _(u"Tags"),
                size = 60,
                values = tuple(results),
            )

@colander.deferred
def deferred_delete_title(node, kw):
    context = kw['context']
    msg = _(u"delete_confirmation_by_typing_title_text",
            default = u"If you're absolutely sure you wish to delete this, type this objects title in the field below: '${obj_title}'",
            mapping = {'obj_title': context.title})
    return msg


def add_translations_node(schema, translations_key, based_on = None, title = _(u"Translations"), description = u""):
    """ Add a section for translations. English will be omitted, since it's the default langauge.
        
        schema
            Where this node should be added. The subsection will be the same as translations_key,
            so the actual schema structure will be at schema[translations_key]

        translations_key
            The key for the translations. We will append this section to the schema, and it must also be used
            as storage for the data. This should contain any previous data stored as well.

        based_on = None
            Specify if you want the widget to be constructed from this attribute. If you have something in the
            schema called 'title' for instance, and you want a field called 'translated_titles' simply add 'title'
            here to copy attributes from that schema node.
    """
    schema[translations_key] = colander.Schema(title = title, description = description)
    if based_on:
        type_cls = schema[based_on].typ.__class__
        for (lang, title) in _get_langs(omit = ('en',)):
            schema[translations_key].add(
                colander.SchemaNode(
                    type_cls(),
                    name = lang,
                    title = title,
                    missing = u"",
                    validator = schema[based_on].validator,
                    widget = schema[based_on].widget,
                )
            )
    else:
        for (lang, title) in _get_langs(omit = ('en',)):
            schema[translations_key].add(
                colander.SchemaNode(
                    colander.String(),
                    name = lang,
                    title = title,
                    missing = u"",
                    widget = deform.widget.TextInputWidget(size = 80),
                )
            )
