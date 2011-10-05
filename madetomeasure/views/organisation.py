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

    @view_config(name='invariant', context=IOrganisation, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def invariant(self):
        root = find_root(self.context)
        question_uid = self.request.GET.get('question_uid', None)

        if question_uid is None and not question_uid in root['questions']:
            self.add_flash_message(_(u"Invalid question uid."))
            url = resource_url(self.context, self.request)
            return HTTPFound(location=url)
            
        question = root['questions'][question_uid]

        schema = CONTENT_SCHEMAS["Translate%s" % question.content_type]()
        schema = schema.bind(context = question,)
        # add default locale
        self.trans_util.add_translation_schema(schema['question_text'], self.trans_util.default_locale_name)
        self.trans_util.add_translations_schema(schema['question_text'])
        
        form = Form(schema, buttons=(self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()

            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            for (lang, value) in appstruct['question_text'].items():
                if value.strip():
                    self.context.set_invariant(question_uid, lang, value)

            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        marker = object()
        appstruct = {}
        for field in schema:
            accessor = getattr(question, "get_%s" % field.name, marker)
            if accessor != marker:
                appstruct[field.name] = accessor()
        # add default locale
        appstruct['question_text'][self.trans_util.default_locale_name] = question.get_title()

        # load local invariants
        if 'question_text' in appstruct:
            for lang in appstruct['question_text']:
                if question_uid in self.context.invariants and lang in self.context.invariants[question_uid]:
                    appstruct['question_text'][lang] = self.context.invariants[question_uid][lang]
                    
        self.response['form'] = form.render(appstruct)
        return self.response
