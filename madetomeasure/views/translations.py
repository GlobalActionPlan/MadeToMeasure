from urllib import unquote

from deform import Form
from deform.exception import ValidationFailure
from pyramid.view import view_config
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from betahaus.pyracont.factories import createSchema

from madetomeasure.interfaces import ILocalQuestions
from madetomeasure.interfaces import IQuestion
from madetomeasure.interfaces import IQuestions
from madetomeasure.interfaces import IQuestionTypes
from madetomeasure.interfaces import IQuestionTranslations
from madetomeasure.interfaces import ISurvey
from madetomeasure.interfaces import ISurveySection
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure import security


class TranslationsView(BaseView):

    @reify
    def trans_util(self):
        return self.request.registry.getUtility(IQuestionTranslations)

    @view_config(name = "translations", context = IQuestions, permission = security.TRANSLATE, renderer = "templates/question_translations.pt")
    @view_config(name = "translations", context = ILocalQuestions, permission = security.TRANSLATE, renderer = "templates/question_translations.pt")
    def question_translations(self):
        lang = self.request.GET.get('lang', None)
        limit_untranslated = self.request.GET.get('limit_untranslated', None)
        translatable_languages = self.trans_util
        self.response['trans_util'] = self.trans_util
        self.response['selected_lang'] = lang
        return self.response

    @view_config(name = "translate", context = IQuestion, renderer = BASE_FORM_TEMPLATE, permission = security.TRANSLATE)
    def translate_question_view(self):
        lang = self.request.GET['lang']
        schema = createSchema(self.context.schemas['translate'])
        schema = schema.bind(context = self.context, request = self.request)
        self.trans_util.add_translation_schema(schema['question_text'], lang)
        form = Form(schema, buttons=(self.buttons['save'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()
        if self.request.method == 'POST':
            if 'save' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    appstruct = form.validate(controls)
                except ValidationFailure, e:
                    self.response['form'] = e.render()
                    return self.response
                for (lang, value) in appstruct['question_text'].items():
                    self.context.set_question_text_lang(value, lang)
            url = unquote(self.request.GET['came_from'])
            return HTTPFound(location = url)
        appstruct = self.context.get_field_appstruct(schema)
        self.response['form'] = form.render(appstruct)
        return self.response

#     @view_config(name = "translate", context = ISurvey, renderer = BASE_FORM_TEMPLATE, permission = security.TRANSLATE)
#     def translate_survey(self):
#         lang = self.request.GET['lang']
#         schema = createSchema(self.context.schemas['translate'])
#         schema = schema.bind(context = self.context, request = self.request)
#         form = Form(schema, buttons=(self.buttons['cancel'], self.buttons['save'],))
#         self.response['form_resources'] = form.get_widget_resources()
#         if self.request.method == 'POST':
#             if 'save' in self.request.POST:
#                 controls = self.request.POST.items()
#                 try:
#                     appstruct = form.validate(controls)
#                 except ValidationFailure, e:
#                     self.response['form'] = e.render()
#                     return self.response
#                 self.context.set_welcome_text(appstruct['welcome_text'], lang)
#                 self.context.set_finished_text(appstruct['finished_text'], lang)
#             url = self.request.resource_url(self.context)
#             return HTTPFound(location = url)
#         appstruct = {}
#         appstruct['welcome_text'] = self.context.get_welcome_text(lang=lang, default=False)
#         appstruct['finished_text'] = self.context.get_finished_text(lang=lang, default=False)
#         self.response['form'] = form.render(appstruct)
#         return self.response

#     @view_config(name = "translate", context = ISurveySection, renderer = BASE_FORM_TEMPLATE, permission = security.TRANSLATE)
#     def translate_survey_section(self):
#         pass
