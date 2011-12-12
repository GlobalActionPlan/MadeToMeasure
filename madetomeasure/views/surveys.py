import csv
import StringIO
from datetime import datetime
from uuid import uuid4

from deform import Form
from deform.exception import ValidationFailure
import colander

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url
from pyramid.traversal import find_root
from pyramid.traversal import find_interface
from pyramid.exceptions import Forbidden
from pyramid.response import Response
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


class SurveysView(BaseView):

    @view_config(name='invitation_emails', context=ISurvey, renderer=BASE_FORM_TEMPLATE, permission=security.MANAGE_SURVEY)
    def invitation_emails_view(self):
        """ Edit email addresses for who should be part of a survey. """
        
        closed_survey = self._closed_survey(self.context)
        
        post = self.request.POST
        if 'cancel' in post or closed_survey:
            if closed_survey:
                self.add_flash_message(_(u"Survey has closed, you can't invite"))
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        schema = CONTENT_SCHEMAS["SurveyInvitation"]()
        schema = schema.bind(context = self.context, request = self.request)
        form = Form(schema, buttons=(self.buttons['send'], self.buttons['cancel']))
        self.response['form_resources'] = form.get_widget_resources()

        if 'send' in post:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response

            emails = set()
            for email in appstruct['emails'].splitlines():
                emails.add(email.strip())
            message = appstruct['message']
            subject = appstruct['subject']

            self.context.send_invitations(self.request, emails, subject, message)

            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        self.response['form'] = form.render()
        return self.response

    def _closed_survey(self, obj):
        if not ISurvey.providedBy(obj):
            raise TypeError("obj must be a Survey")
        end_time = obj.get_field_value('end_time', None)
        if not end_time:
            return False
        return self.survey_dt.utcnow() > end_time

    @view_config(name='participants', context=ISurvey, renderer='templates/survey_participans.pt', permission=security.MANAGE_SURVEY)
    def participants_view(self):
        """ Overview of participants. """
        self.response['participants'] = participants = self.context.get_participants_data()
        not_finished = [x for x in participants if x['finished']<100]
        self.response['not_finished'] = not_finished
        self.response['closed_survey'] = self._closed_survey(self.context)

        schema = CONTENT_SCHEMAS["SurveyReminder"]()
        schema = schema.bind(context = self.context, request = self.request)
        form = Form(schema, buttons=(self.buttons['send'],))
        self.response['form_resources'] = form.get_widget_resources()

        post = self.request.POST
        if 'send' in post:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response

            for participant in not_finished:
                # a participant with less then 100% completion will receive the invite ticket again with specified message
                ticket_uid = participant['uid']
                email = self.context.tickets[ticket_uid]
                self.context.send_invitation_email(self.request, email, ticket_uid, appstruct['subject'], appstruct['message'])

            self.add_flash_message(_(u"Reminder has been sent"))

        self.response['form'] = form.render()
        return self.response

    def _survey_error_msg(self, exeption):
        if exeption.not_started:
            
            start_time = self.survey_dt.dt_format(self.context.get_field_value('start_time', None), format='full')
            msg = _(u"not_started_error",
                    default=_(u"Survey has not started yet, it will start at ${start_time}"),
                    mapping={'start_time':start_time})
        if exeption.ended:
            end_time = self.survey_dt.dt_format(self.context.get_field_value('end_time', None), format='full')
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
        available_languages = self.context.get_available_languages()
        schema = CONTENT_SCHEMAS["SurveyLangugage"]()
        schema = schema.bind(languages = available_languages, context = self.context, request = self.request)
        form = Form(schema, buttons=(self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()

        post = self.request.POST
        if 'save' in post:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            selected_language = appstruct['selected_language']

        # if no language is selected and survey only has one language available set it as the select language
        if not selected_language and len(available_languages) == 1:
            selected_language = tuple(available_languages)[0]

        # redirect to first section if language is selected
        if selected_language:
            self.request.response.set_cookie('_LOCALE_', value=selected_language)

            participant_uid = self.context.start_survey(self.request)
            self.context.set_participant_language(participant_uid, selected_language)

            #All good so far, let's redirect to welcome screen of the survey
            url = resource_url(self.context, self.request)
            url += "welcome?uid=%s" % participant_uid
            # adding header so cookie is set
            return HTTPFound(location=url, headers=self.request.response.headers)
            
        self.response['form'] = form.render()
        return self.response
            
    @view_config(name="welcome", context=ISurvey, renderer='templates/participant_welcome.pt')
    def welcome(self):
        self.context.check_open()
        participant_uid = self.request.params.get('uid')
        if not participant_uid in self.context.tickets:
            raise Forbidden("Invalid ticket")

        lang = None
        if '_LOCALE_' in self.request.cookies:
            lang = self.request.cookies['_LOCALE_']

        welcome_text = self.context.get_welcome_text(lang=lang)
        post = self.request.POST

        # survey has no welcome text or the user pushed next, let's redirect to the first section of the survey
        if not welcome_text or 'next' in post:
            # url for the first section
            if len(self.context.order) > 0:
                section_id = self.context.order[0]
                url = resource_url(self.context[section_id], self.request)
                url += "do?uid=%s" % participant_uid
            else:
                url = resource_url(self.context, self.request)
                url += "finished"
            return HTTPFound(location=url)

        form = Form(colander.Schema(), buttons=(self.buttons['next'],))
        self.response['form_resources'] = form.get_widget_resources()
        self.response['form'] = form.render()
        self.response['text'] = welcome_text
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
        if 'next' in post:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            self.context.update_question_responses(participant_uid, appstruct)
            if next_section:
                url = resource_url(next_section, self.request)
                url += "do?uid=%s" % participant_uid
            else:
                url = resource_url(self.context.__parent__, self.request)
                url += "finished"
            return HTTPFound(location=url)

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
        lang = None
        if '_LOCALE_' in self.request.cookies:
            lang = self.request.cookies['_LOCALE_']
        self.response['text'] = self.context.get_finished_text(lang=lang)
        return self.response

    @view_config(name="results", context=ISurvey, renderer='templates/results.pt', permission=security.VIEW)
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

    @view_config(context=ISurveySection, renderer='templates/survey_form.pt', permission=security.VIEW)
    def show_dummy_form_view(self):
        schema = colander.Schema()
        self.context.append_questions_to_schema(schema, self.request)
        form = Form(schema)
        self.response['form_resources'] = form.get_widget_resources()
        self.response['dummy_form'] = form.render()
        return self.response

    @view_config(name="translations", context=ISurvey, renderer='templates/survey_translations.pt', permission=security.VIEW)
    def translations(self):
        """ Shows the amount of translations
        """
        self.response['context'] = self.context
        self.response['texts'] = self.context.untranslated_texts()
        self.response['languages'] = self.context.untranslated_languages()
        return self.response

    @view_config(context=ISurvey, renderer='templates/survey_admin_view.pt', permission=security.VIEW)
    def survey_admin_view(self):
        start_time = self.context.get_field_value('start_time', None)
        end_time = self.context.get_field_value('end_time', None)
        if start_time:
            start_time = self.survey_dt.dt_format(start_time)
        if end_time:
            end_time = self.survey_dt.dt_format(end_time)
        self.response['start_time'] = start_time
        self.response['end_time'] = end_time
        #Is survey active?
        try:
            self.context.check_open()
            msg = _(u"The survey is currently open.")
            self.response['survey_state_msg'] = msg
        except SurveyUnavailableError as e:
            msg = self._survey_error_msg(e)
            self.response['survey_state_msg'] = msg

        return self.response

    @view_config(name='reorder', context=ISurvey, renderer='templates/reorder_surveysection.pt', permission=security.EDIT)
    def reorder_surveysection(self):
        post = self.request.POST
        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        if 'save' in post:
            controls = self.request.POST.items()
            sections = []
            for (k, v) in controls:
                if k == 'sections':
                    sections.append(v)
            self.context.order = sections
            self.add_flash_message(_('Order updated'))

        form = Form(colander.Schema())
        self.response['form_resources'] = form.get_widget_resources()
        self.response['dummy_form'] = form.render()
        return self.response
        
    @view_config(name='reorder', context=ISurveySection, renderer='templates/reorder_questions.pt', permission=security.EDIT)
    def reorder_questions(self):
        post = self.request.POST

        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        if 'save' in post:
            controls = self.request.POST.items()
            questions = []
            for (k, v) in controls:
                if k == 'questions':
                    questions.append(v)
                        
            self.context.set_order(questions)
            self.add_flash_message(_('Order updated'))
            
        form = Form(colander.Schema())
        self.response['form_resources'] = form.get_widget_resources()
        self.response['dummy_form'] = form.render()
        return self.response
        
    @view_config(name='translate', context=ISurvey, renderer='templates/survey_translate.pt', permission=security.TRANSLATE)
    def translate_view(self):

        lang = self.request.GET['lang']
        schema = CONTENT_SCHEMAS["Translate%s" % self.context.content_type]()
        schema = schema.bind(context = self.context, request = self.request)
        form = Form(schema, buttons=(self.buttons['cancel'], self.buttons['save'],))
        self.response['form_resources'] = form.get_widget_resources()

        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            self.context.set_welcome_text(appstruct['welcome_text'], lang)
            self.context.set_finished_text(appstruct['finished_text'], lang)
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        appstruct = {}
        appstruct['welcome_text'] = self.context.get_welcome_text(lang=lang, default=False)
        appstruct['finished_text'] = self.context.get_finished_text(lang=lang, default=False)

        self.response['form'] = form.render(appstruct)
        self.response['welcome_text'] = self.context.get_welcome_text()
        self.response['finished_text'] = self.context.get_finished_text()
        return self.response
        
    @view_config(name='export.csv', context=ISurvey, permission=security.VIEW)
    def export(self):
        """ Results screen
        """
        output = StringIO.StringIO()
        writer = csv.writer(output)
        writer.writerow([self.context.title.encode('utf-8')])
        languages = self.context.get_language_participants
        lrow = [_(u"Languages").encode('utf-8'), _(u"Total").encode('utf-8')]
        langs = set(languages.keys()) | set(self.context.get_available_languages())
        for lang in langs:
            lrow.append(u"%s (%s)" % (self.trans_util.title_for_code(lang).encode('utf-8'), 
                                      self.trans_util.title_for_code_default(lang).encode('utf-8')))
        writer.writerow(lrow)
        lrow = [""]
        for lang in langs:
            if lang in languages:
                lrow.append(len(languages[lang]))
            else:
                lrow.append(0)
        lrow.insert(1, sum(lrow[1:]))
        writer.writerow(lrow)
        writer.writerow([])

        def _get_questions(section):
            results = {}
            for name in section.question_ids:
                question = section.question_object_from_id(name)
                if question.get_question_type() not in results:
                    results[question.get_question_type()] = {}
                    results[question.get_question_type()]['obj'] = getUtility(IQuestionNode, name=question.get_question_type())
                    results[question.get_question_type()]['questions'] = []

                results[question.get_question_type()]['questions'].append(question)
            return results

        for section in self.context.values():
            writer.writerow(['Section: %s' % section.title.encode('utf-8')])
            writer.writerow([])

            for qtype in _get_questions(section).values():
                writer.writerow(qtype['obj'].csv_header())

                for question in qtype['questions']:
                    titles = []
                    for lang in self.context.get_available_languages():
                        title = question.get_title(lang=lang).encode('utf-8')
                        if title:
                            titles.append(title)
                    title = ", ".join(titles)

                    for qresult in question.csv_export(section.question_format_results().get(question.__name__)):
                        qrow = [title]
                        qrow.extend(qresult)
                        writer.writerow(qrow)
                        title = ""

        contents = output.getvalue()
        output.close()
        response = Response(content_type='text/csv',
                            body=contents)
        return response
        
    @view_config(name='clone', context=ISurvey, renderer=BASE_FORM_TEMPLATE, permission=security.EDIT)
    def clone(self):
        """ Cloning survey
        """
        
        if 'cancel' in self.request.POST:
            url = resource_url(self.context, self.request)
            return HTTPFound(location = url)

        schema = CONTENT_SCHEMAS["Clone%s" % self.context.content_type]()
        schema = schema.bind(context = self.context, request = self.request)
        
        form = Form(schema, buttons=(self.buttons['save'], self.buttons['cancel'], ))
        self.response['form_resources'] = form.get_widget_resources()
        
        if 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            
            new_survey = self.context.clone(appstruct['title'], appstruct['destination'])
            
            url = resource_url(new_survey, self.request)
            return HTTPFound(location = url)

        appstruct = {}
        appstruct['title'] = "%s_clone_%s" % (self.context.title, datetime.now())

        self.response['form'] = form.render(appstruct)
        return self.response
