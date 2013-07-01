from deform import Form
from deform.exception import ValidationFailure
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import find_root
from pyramid.response import Response
from pyramid.renderers import render
from betahaus.pyracont.factories import createSchema

from madetomeasure.interfaces import IOrganisation
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure import security


class OrganisationView(BaseView):
    @view_config(context=IOrganisation, renderer='templates/organisation_view.pt', permission=security.VIEW)
    def admin_listing_view(self):
        return self.response

    @view_config(name='variant', context=IOrganisation, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def variant(self):
        root = find_root(self.context)
        question_uid = self.request.GET.get('question_uid', None)

        if question_uid is None and not question_uid in root['questions']:
            self.add_flash_message(_(u"Invalid question uid."))
            url = self.request.resource_url(self.context)
            return HTTPFound(location=url)
            
        question = root['questions'][question_uid]

        schema = createSchema(question.schemas['translate'])
        schema.title = _(u"Edit question variant for this organisation")
        schema = schema.bind(context = question, request = self.request)
        # add default locale
        description = question.get_original_title()
        descriptions = question.get_question_text()
        self.trans_util.add_translation_schema(schema['question_text'], self.trans_util.default_locale_name, description=description)
        self.trans_util.add_translations_schema(schema['question_text'], self.context, descriptions=descriptions, only_with_description=True)
        
        form = Form(schema, action = self.request.url, buttons=(self.buttons['save'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            for (lang, value) in appstruct['question_text'].items():
                self.context.set_variant(question_uid, lang, value)

            url = self.request.resource_url(self.context, 'variants')
            return HTTPFound(location = url)
        
        if 'cancel' in self.request.POST:
            url = self.request.resource_url(self.context, 'variants')
            return HTTPFound(location = url)

        appstruct = {'question_text': {}}
        # load local variants
        for lang in self.trans_util.available_languages:
            if question_uid in self.context.variants and lang in self.context.variants[question_uid]:
                appstruct['question_text'][lang] = self.context.variants[question_uid][lang]
        
        self.response['form'] = form.render(appstruct)
        return self.response

    @view_config(name='variant', context=IOrganisation, permission=security.EDIT, xhr=True)
    def variant_ajax(self):
        response = self.variant()
        if isinstance(response, HTTPFound):
            #Override redirect
            question_uid = self.request.GET.get('question_uid', None)
            question = self.root['questions'][question_uid]
            response = {'question_text': question.get_title(context = self.context),
                        'is_variant': question.is_variant}
            return Response(render("json", response, request = self.request))
        return Response(render("templates/ajax_form.pt", response, request = self.request))
