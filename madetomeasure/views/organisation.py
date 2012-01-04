from uuid import uuid4

from deform import Form
from deform.exception import ValidationFailure
import colander

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url
from pyramid.traversal import find_root
from pyramid.exceptions import Forbidden
from zope.component import getUtility

from madetomeasure.interfaces import *
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BASE_VIEW_TEMPLATE
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure.models import CONTENT_TYPES
from madetomeasure.schemas import CONTENT_SCHEMAS
from madetomeasure.models.exceptions import SurveyUnavailableError
from madetomeasure import security


class OrganisationView(BaseView):
    @view_config(context=IOrganisation, renderer='templates/organisation_view.pt', permission=security.VIEW)
    def admin_listing_view(self):
        return self.response


    @view_config(name='variants', context=IOrganisation, renderer='templates/organisation_variants.pt', permission=security.EDIT)
    def variants(self):
        root = find_root(self.context)
        
        def _get_variants(question):
            variants = []
            if question.__name__ in self.context.variants:
                for lang in self.context.variants[question.__name__]:
                    variants.append(self.trans_util.title_for_code(lang))
            variants = sorted(variants)
            return ", ".join(variants)
        
        self.response['get_variants'] = _get_variants
        self.response['url'] = resource_url(self.context, self.request) + 'variant?question_uid='
        self.response['questions'] = root['questions']
        
        return self.response

    @view_config(name='variant', context=IOrganisation, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def variant(self):
        root = find_root(self.context)
        question_uid = self.request.GET.get('question_uid', None)

        if question_uid is None and not question_uid in root['questions']:
            self.add_flash_message(_(u"Invalid question uid."))
            url = resource_url(self.context, self.request)
            return HTTPFound(location=url)
            
        question = root['questions'][question_uid]

        schema = CONTENT_SCHEMAS["Translate%s" % question.content_type]()
        schema = schema.bind(context = question, request = self.request)
        # add default locale
        description = question.get_title()
        descriptions = question.get_question_text()
        self.trans_util.add_translation_schema(schema['question_text'], self.trans_util.default_locale_name, description=description)
        self.trans_util.add_translations_schema(schema['question_text'], descriptions=descriptions)
        
        form = Form(schema, buttons=(self.buttons['save'],))
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

            url = "%svariants" % resource_url(self.context, self.request)
            return HTTPFound(location = url)

        appstruct = {'question_text': {}}
        # load local variants
        for lang in self.trans_util.available_languages:
            if question_uid in self.context.variants and lang in self.context.variants[question_uid]:
                appstruct['question_text'][lang] = self.context.variants[question_uid][lang]
        
        self.response['form'] = form.render(appstruct)
        return self.response
