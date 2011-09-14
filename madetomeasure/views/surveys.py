from uuid import uuid4

from deform import Form
from deform.exception import ValidationFailure

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url
from pyramid.traversal import find_root
from pyramid.exceptions import Forbidden

from madetomeasure.interfaces import *
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.models import CONTENT_TYPES
from madetomeasure.schemas import CONTENT_SCHEMAS
from madetomeasure.models.app import generate_slug
from madetomeasure.schemas.surveys import DoSurveySchema


class SurveysView(BaseView):

    @view_config(name='add', context=ISurveys, renderer='templates/form.pt')
    @view_config(name='add', context=ISurvey, renderer='templates/form.pt')
    def add_view(self):
        """ Add Survey and Survey Section. """
        #FIXME: Check permissions
        type_to_add = self.request.GET.get('content_type')
        if type_to_add not in self.addable_types():
            raise ValueError("No content type called %s" % type_to_add)

        schema = CONTENT_SCHEMAS["Add%s" % type_to_add]()
        schema = schema.bind()
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
            
            obj = CONTENT_TYPES[type_to_add]()
            for (k, v) in appstruct.items():
                mutator = getattr(obj, 'set_%s' % k)
                mutator(v)
            
            name = generate_slug(self.context, obj.get_title())
            self.context[name] = obj
    
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        self.response['form'] = form.render()
        return self.response


    @view_config(name='edit', context=ISurvey, renderer='templates/form.pt')
    @view_config(name='edit', context=ISurveySection, renderer='templates/form.pt')
    def edit_view(self):
        #FIXME: Check permissions
        
        def _question_types():
            #FIXME: Handle several?
            if hasattr(self.context, 'get_question_type'):
                return [self.context.get_question_type()]

        schema = CONTENT_SCHEMAS["Edit%s" % self.context.content_type]()
        schema = schema.bind(context = self.context,
                             question_types = _question_types())
                
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
            
            for (k, v) in appstruct.items():
                mutator = getattr(self.context, 'set_%s' % k)
                mutator(v)
                
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        marker = object()
        appstruct = {}
        for field in schema:
            accessor = getattr(self.context, "get_%s" % field.name, marker)
            if accessor != marker:
                appstruct[field.name] = accessor()

        self.response['form'] = form.render(appstruct)
        return self.response
    
    @view_config(name='invitation_emails', context=ISurvey, renderer='templates/form.pt')
    def invitation_emails_view(self):
        """ Edit email addresses for who should be part of a survey. """
        #FIXME: Check permissions

        schema = CONTENT_SCHEMAS["SurveyInvitation"]()
        schema = schema.bind()
        form = Form(schema, buttons=(self.buttons['save'], self.buttons['send']))
        self.response['form_resources'] = form.get_widget_resources()
        
        post = self.request.POST
        if 'save' in post or 'send' in post:
            controls = self.request.POST.items()

            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            for (k, v) in appstruct.items():
                mutator = getattr(self.context, 'set_%s' % k)
                mutator(v)
            
            if 'send' in post:
                self.context.send_invitations(self.request)
                
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        marker = object()
        appstruct = {}
        for field in schema:
            accessor = getattr(self.context, "get_%s" % field.name, marker)
            if accessor != marker:
                appstruct[field.name] = accessor()

        self.response['form'] = form.render(appstruct)
        return self.response

    @view_config(name="do", context=ISurvey, renderer='templates/form.pt')
    def start_survey_view(self):
        """ This view simply redirects to the first section.
            This starts the survey for this participant.
        """
        participant_uid = self.context.start_survey(self.request)
        
        #All good so far, let's redirect to the first section of the survey
        section_id = self.context.order[0]
        url = resource_url(self.context[section_id], self.request)
        url += "do?uid=%s" % participant_uid
        return HTTPFound(location=url)
        
    @view_config(name="do", context=ISurveySection, renderer='templates/form.pt')
    def do_survey_section_view(self):
        """ Where participants go to tell us about their life... """
        survey = self.context.__parent__

        participant_uid = self.request.params.get('uid')
        if not participant_uid in survey.tickets:
            raise Forbidden("Invalid ticket")

        schema = DoSurveySchema().bind(participant_uid=participant_uid,)
        
        form = Form(schema, buttons=(self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()
        self.response['form'] = form.render()
        return self.response
        