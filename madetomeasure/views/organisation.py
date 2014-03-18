from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.decorator import reify
from betahaus.pyracont.factories import createSchema

from madetomeasure.interfaces import IOrganisation
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BaseForm
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure import security


class OrganisationView(BaseView):
    @view_config(context=IOrganisation, renderer='templates/organisation_view.pt', permission=security.VIEW)
    def admin_listing_view(self):
        return self.response


class OrganisationForm(BaseForm):

    @property
    def form_options(self):
        return dict(action = self.request.url)

    @property
    def buttons(self):
        return (self.button_save, self.button_cancel,)

    @reify
    def schema(self):
        schema = createSchema(self.question.schemas['translate'])
        schema.title = _(u"Edit question variant for this organisation")
        #This odd stuff is due to the translation behaviour in combination with reify. Unclear why, but if it's not
        #reinitialized as a new copy, the old schema is persistent somehow.
        schema = schema.bind(**self.get_bind_data())
        # add default locale
        description = self.question.get_original_title()
        descriptions = self.question.get_question_text()
        self.trans_util.add_translation_schema(schema['question_text'], self.trans_util.default_locale_name, description=description)
        self.trans_util.add_translations_schema(schema['question_text'], self.context, descriptions=descriptions, only_with_description=True)
        return schema

    @reify
    def question(self):
        question_name = self.request.GET.get('question_name', None)
        globalquestions = self.root['questions']
        if question_name not in globalquestions:
            raise HTTPForbidden(_(u"Invalid question name."))
        return globalquestions[question_name]

    def get_bind_data(self):
        return {'context': self.question, 'request': self.request, 'view': self}

    def appstruct(self):
        qname = self.question.__name__
        appstruct = {'question_text': {}}
        # load local variants
        for lang in self.trans_util.available_languages:
            if qname in self.context.variants and lang in self.context.variants[qname]:
                appstruct['question_text'][lang] = self.context.variants[qname][lang]
        return appstruct

    @view_config(name='variant', context = IOrganisation, renderer = BASE_FORM_TEMPLATE,
                 permission = security.EDIT, xhr = False)
    @view_config(name='variant', context = IOrganisation, renderer = "madetomeasure:views/templates/ajax_form.pt",
                 permission = security.EDIT, xhr = True)
    def variant(self):
        return super(OrganisationForm, self).__call__()

    def save_success(self, appstruct):
        for (lang, value) in appstruct['question_text'].items():
            self.context.set_variant(self.question.__name__, lang, value)
        if self.request.is_xhr:
            response = {'question_text': self.question.get_title(context = self.context),
                        'is_variant': self.question.is_variant}
            return Response(render("json", response, request = self.request))
        else:
            url = self.request.resource_url(self.context, 'variants')
            return HTTPFound(location = url)

#     def variant_ajax(self):
#         """ Variants should only work for global questions! """
#         response = self.variant()
#         if isinstance(response, HTTPFound):
#             #Override redirect
#             question_name = self.request.GET.get('question_name', None)
#             question = self.root['questions'][question_name]
#             response = {'question_text': question.get_title(context = self.context),
#                         'is_variant': question.is_variant}
#             return Response(render("json", response, request = self.request))
#         return Response(render("templates/ajax_form.pt", response, request = self.request))




#     def _variant(self):
#         question_name = self.request.GET.get('question_name', None)
#         globalquestions = self.root['questions']

#         if question_name not in globalquestions:
#             self.add_flash_message(_(u"Invalid question name."))
#             url = self.request.resource_url(self.context)
#             return HTTPFound(location=url)
# 
#         question = globalquestions[question_name]
#         schema = createSchema(question.schemas['translate'])
#         schema.title = _(u"Edit question variant for this organisation")
#         schema = schema.bind(context = question, request = self.request)
#         # add default locale
#         description = question.get_original_title()
#         descriptions = question.get_question_text()
#         self.trans_util.add_translation_schema(schema['question_text'], self.trans_util.default_locale_name, description=description)
#         self.trans_util.add_translations_schema(schema['question_text'], self.context, descriptions=descriptions, only_with_description=True)
        
#         form = Form(schema, action = self.request.url, buttons=(self.buttons['save'], self.buttons['cancel']))
#         self.response['form_resources'] = form.get_widget_resources()
#         
#         if 'save' in self.request.POST:
#             controls = self.request.POST.items()
#             try:
#                 appstruct = form.validate(controls)
#             except ValidationFailure, e:
#                 self.response['form'] = e.render()
#                 return self.response
#             for (lang, value) in appstruct['question_text'].items():
#                 self.context.set_variant(question_name, lang, value)
#             url = self.request.resource_url(self.context, 'variants')
#             return HTTPFound(location = url)
#         
#         if 'cancel' in self.request.POST:
#             url = self.request.resource_url(self.context, 'variants')
#             return HTTPFound(location = url)
# 
#         appstruct = {'question_text': {}}
#         # load local variants
#         for lang in self.trans_util.available_languages:
#             if question_name in self.context.variants and lang in self.context.variants[question_name]:
#                 appstruct['question_text'][lang] = self.context.variants[question_name][lang]
#         
#         self.response['form'] = form.render(appstruct)
#         return self.response
# 
#     @view_config(name='variant', context=IOrganisation, permission=security.EDIT, xhr=True)
#     def variant_ajax(self):
#         """ Variants should only work for global questions! """
#         response = self.variant()
#         if isinstance(response, HTTPFound):
#             #Override redirect
#             question_name = self.request.GET.get('question_name', None)
#             question = self.root['questions'][question_name]
#             response = {'question_text': question.get_title(context = self.context),
#                         'is_variant': question.is_variant}
#             return Response(render("json", response, request = self.request))
#         return Response(render("templates/ajax_form.pt", response, request = self.request))
