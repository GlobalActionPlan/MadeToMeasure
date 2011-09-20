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


class SurveysView(BaseView):

    @view_config(name='invitation_emails', context=ISurvey, renderer=BASE_FORM_TEMPLATE)
    def invitation_emails_view(self):
        """ Edit email addresses for who should be part of a survey. """
        #FIXME: Check permissions
        post = self.request.POST
        if 'cancel' in post:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)


        schema = CONTENT_SCHEMAS["SurveyInvitation"]()
        schema = schema.bind()
        form = Form(schema, buttons=(self.buttons['save'], self.buttons['send'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()

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

    @view_config(name='participants', context=ISurvey, renderer='templates/survey_participans.pt')
    def participants_view(self):
        """ Overview of participants. """
        #FIXME: Check permissions
        
        self.response['participants'] = self.context.get_participants_data()
        
        schema = CONTENT_SCHEMAS["SurveyReminder"]()
        schema = schema.bind()
        form = Form(schema, buttons=(self.buttons['send'],))
        self.response['form_resources'] = form.get_widget_resources()
        
        post = self.request.POST
        if 'send' in post:
            controls = self.request.POST.items()

            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            participants = self.context.get_participants_data()
            for participant in participants:
                # a participant with less then 100% completion will resive the invite ticket again with specified message
                if participant['finished'] < 100:
                    ticket = participant['uid']
                    email = self.context.tickets[ticket]
                    self.context.send_invitation_email(self.request, email, ticket, appstruct['message'])
                    
            self.add_flash_message(_(u"Reminder has been sent"))
        
        self.response['form'] = form.render()
        
        return self.response

    def _survey_error_msg(self, exeption):
        if exeption.not_started:
            start_time = self.survey_dt.dt_format(self.context.get_start_time(), format='full')
            msg = _(u"not_started_error",
                    default=_(u"Survey has not started yet, it will start at ${start_time}"),
                    mapping={'start_time':start_time})
        if exeption.ended:
            end_time = self.survey_dt.dt_format(self.context.get_end_time(), format='full')
            msg = _(u"ended_error",
                    default=_(u"Survey has ended, it closed at ${end_time}"),
                    mapping={'end_time':end_time})
        return msg

    @view_config(name="unavailable", context=ISurvey, renderer=BASE_VIEW_TEMPLATE)
    def unavailable_view(self):
        """ Renders when a survey is unavailable. """
        return self.response

    @view_config(name="do", context=ISurvey, renderer=BASE_FORM_TEMPLATE)
    def start_survey_view(self):
        """ This view askes the participant which language it wants and redirects to the first section.
            This starts the survey for this participant.
        """

        try:
            self.context.check_open()
        except SurveyUnavailableError as e:
            msg = self._survey_error_msg(e)
            self.add_flash_message(msg)
            url = resource_url(self.context, self.request) + 'unavailable'
            return HTTPFound(location=url)
        
        selected_language = None
        
        schema = CONTENT_SCHEMAS["SurveyLangugage"]()
        schema = schema.bind(languages = self.context.get_available_languages())
        form = Form(schema, buttons=(self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()
        
        post = self.request.POST
        if 'save' in post:
            controls = self.request.POST.items()

            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            selected_language = appstruct['selected_language']
                
        # if no language is selected and survey only has one lanugage available set it as the seletect language
        if not selected_language and len(self.context.get_available_languages()) == 1:
            selected_language = self.context.get_available_languages()[0]

        # redirect to first section if language is selected or if previously selected language is available here as well
        if selected_language or 'lang' in self.request.session and self.request.session['lang'] in self.context.get_available_languages():
            if selected_language:
                self.request.session['lang'] = selected_language

            participant_uid = self.context.start_survey(self.request)
            
            #All good so far, let's redirect to the first section of the survey
            section_id = self.context.order[0]
            url = resource_url(self.context[section_id], self.request)
            url += "do?uid=%s" % participant_uid
            return HTTPFound(location=url)

        self.response['form'] = form.render()
        
        return self.response

    def _next_section(self):
        """ Return next section object if there is one.
        """
        parent = self.context.__parent__
        section_order = tuple(parent.order)
        cur_index = section_order.index(self.context.__name__)
        try:
            next_name = section_order[cur_index+1]
            return parent[next_name]
        except IndexError:
            return

    def _previous_section(self):
        """ Return previous section object if there is one.
        """
        parent = self.context.__parent__
        section_order = tuple(parent.order)
        cur_index = section_order.index(self.context.__name__)
        if cur_index == 0:
            #Since -1 is a valid index :)
            return
        try:
            previous_name = section_order[cur_index-1]
            return parent[previous_name]
        except IndexError:
            return        

    @view_config(name="do", context=ISurveySection, renderer='templates/survey_form.pt')
    def do_survey_section_view(self):
        """ Where participants go to tell us about their life... """
        survey = self.context.__parent__
        survey.check_open()
                
        participant_uid = self.request.params.get('uid')
        if not participant_uid in survey.tickets:
            raise Forbidden("Invalid ticket")

        schema = colander.Schema()
        self.context.append_questions_to_schema(schema, self.request)
        
        next_section = self._next_section()
        previous_section = self._previous_section()
        
        buttons = [self.buttons['next']]
        if previous_section:
            buttons.insert(0, self.buttons['previous'])
        form = Form(schema, buttons=buttons)
        self.response['form_resources'] = form.get_widget_resources()

        post = self.request.POST
        if 'next' in post or 'previous' in post:
            controls = self.request.POST.items()

            try:
                #appstruct is deforms convention. It will be the submitted data in a dict.
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            self.context.update_question_responses(participant_uid, appstruct)
            
            if 'next' in post:
                if next_section:
                    url = resource_url(next_section, self.request)
                    url += "do?uid=%s" % participant_uid
                else:
                    url = resource_url(self.context.__parent__, self.request)
                    url += "finished"
            if 'previous' in post:
                url = resource_url(previous_section, self.request)
                url += "do?uid=%s" % participant_uid
            return HTTPFound(location=url)
            
        appstruct = self.context.response_for_uid(participant_uid)

        self.response['form'] = form.render(appstruct)
        return self.response


    @view_config(name="finished", context=ISurvey, renderer='templates/participant_finished.pt')
    def finished_survey_view(self):
        """ The thank-you screen
        """
        self.response['text'] = self.context.get_finished_text()
        return self.response

    @view_config(name="results", context=ISurvey, renderer='templates/results.pt')
    def results_view(self):
        """ Results screen
        """

        sections = []
        section_results = {}
        #Loop through all sections and save them in sections
        #Also add section data with section.__name__ as key
        for section in self.context.values():
            sections.append(section)
            section_results[section.__name__] = section.question_format_results()

        def _get_questions(section):
            results = []
            for name in section.question_ids:
                results.append(section.question_object_from_id(name))
            return results
        
        self.response['sections'] = sections
        self.response['section_results'] = section_results
        self.response['get_questions_for_section'] = _get_questions
        return self.response
        
    @view_config(context=ISurveySection, renderer='templates/survey_form.pt')
    def show_dummy_form_view(self):
        schema = colander.Schema()
        self.context.append_questions_to_schema(schema, self.request)
        
        form = Form(schema)
        self.response['form_resources'] = form.get_widget_resources()
        
        self.response['dummy_form'] = form.render()
        return self.response
        
    @view_config(name="translations", context=ISurvey, renderer='templates/survey_translations.pt')
    def translations(self):
        """ Shows the amount of translations
        """
        trans_util = getUtility(IQuestionTranslations)
        
        # get available for survey
        available_languages = self.context.get_available_languages()
        # remove default language
        available_languages.remove(trans_util.default_locale_name)
        
        languages = {}
        for language in available_languages:
            for section in self.context.values():
                questions = []
                for name in section.question_ids:
                    question = section.question_object_from_id(name)
                    if not language in question.get_question_text():
                        questions.append(question)
            if questions:
                languages[language] = {
                        'name': trans_util.lang_names[language],
                        'questions': questions,
                    }
        
        self.response['languages'] = languages
        return self.response

    @view_config(context=ISurvey, renderer='templates/survey_admin_view.pt')
    def survey_admin_view(self):
        start_time = self.context.get_start_time()
        end_time = self.context.get_end_time()
        self.response['start_time'] = None
        self.response['end_time'] = None
        if start_time:
            self.response['start_time'] = self.survey_dt.dt_format(start_time)
        if end_time:
            self.response['end_time'] = self.survey_dt.dt_format(end_time)
        
        #Is survey active?
        try:
            self.context.check_open()
            msg = _(u"The survey is currently open.")
            self.response['survey_state_msg'] = msg
        except SurveyUnavailableError as e:
            msg = self._survey_error_msg(e)
            self.response['survey_state_msg'] = msg

