import csv
import StringIO

import colander
from deform import Form
from deform.exception import ValidationFailure
from pyramid.view import view_config
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound
from pyramid.traversal import find_interface
from pyramid.exceptions import Forbidden
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED
from betahaus.pyracont.factories import createSchema
from js.jqueryui import ui_sortable

from madetomeasure.interfaces import IOrganisation
from madetomeasure.interfaces import IChoiceQuestionType
from madetomeasure.interfaces import IMultiChoiceQuestionType
from madetomeasure.interfaces import ISurvey
from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView
from madetomeasure.views.base import BaseForm
from madetomeasure.views.base import BASE_FORM_TEMPLATE
from madetomeasure.models.exceptions import SurveyUnavailableError
from madetomeasure.interfaces import ISurveySection
from madetomeasure.interfaces import ITextSection
from madetomeasure.fanstaticlib import manage_questions
from madetomeasure import security


class SurveysView(BaseView):

    @view_config(name='participants', context=ISurvey, renderer='templates/survey_participans.pt', permission=security.MANAGE_SURVEY)
    def participants_view(self):
        """ Overview of participants. """
        self.response['participants'] = participants = self.context.get_participants_data()
        not_finished = [x for x in participants if x['finished']<100]
        self.response['not_finished'] = not_finished
        self.response['closed_survey'] = self._closed_survey(self.context)
        schema = createSchema(self.context.schemas['reminder'])
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

    @view_config(name="unavailable", context=ISurvey, renderer="templates/survey_unavailable.pt")
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
            self.add_flash_message(e.msg)
            url = self.request.resource_url(self.context, 'unavailable')
            return HTTPFound(location=url)
        selected_language = None
        available_languages = self.context.get_available_languages()
        schema = createSchema(self.context.schemas['language'])
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
            self.set_lang(selected_language)
            participant_uid = self.context.start_survey(self.request)
            self.context.set_participant_language(participant_uid, selected_language)
            #Redirect to first page
            if self.context.order:
                section_id = self.context.order[0]
                url = self.request.resource_url(self.context[section_id], 'do', query = {'uid': participant_uid})
            else:
                self.add_flash_message(_(u"There aren't any pages in this survey"))
                url = self.request.resource_url(self.context)
            # adding header so cookie is set
            return HTTPFound(location = url, headers = self.request.response.headers)
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
        if 'next' in post:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure, e:
                self.response['form'] = e.render()
                return self.response
            self.context.update_question_responses(participant_uid, appstruct)
            if next_section:
                url = self.request.resource_url(next_section, 'do', query = {'uid': participant_uid})
            else:
                url = self.request.resource_url(survey, 'finished')
            return HTTPFound(location=url)
        if 'previous' in post:
            url = self.request.resource_url(previous_section, 'do', query = {'uid': participant_uid})
            return HTTPFound(location=url)
        appstruct = self.context.response_for_uid(participant_uid)
        self.response['form'] = form.render(appstruct)
        return self.response

    @view_config(name="do", context=ITextSection, renderer='templates/survey_text_page.pt')
    def do_text_section_view(self):
        """ Text section, should be included in the regular do view in time. """
        survey = self.context.__parent__
        survey.check_open()
        participant_uid = self.request.params.get('uid')
        if not participant_uid in survey.tickets:
            raise Forbidden("Invalid ticket")
        schema = colander.Schema()
        next_section = self._next_section()
        previous_section = self._previous_section()
        buttons = [self.buttons['next']]
        if previous_section:
            buttons.insert(0, self.buttons['previous'])
        form = Form(schema, buttons=buttons)
        self.response['form_resources'] = form.get_widget_resources()
        post = self.request.POST
        if 'next' in post:
            if next_section:
                url = self.request.resource_url(next_section, 'do', query = {'uid': participant_uid})
            else:
                url = self.request.resource_url(survey, 'finished')
            return HTTPFound(location = url)
        if 'previous' in post:
            url = self.request.resource_url(previous_section, 'do', query = {'uid': participant_uid})
            return HTTPFound(location = url)
        self.response['form'] = form.render()
        return self.response

    @view_config(name="finished", context=ISurvey, renderer='templates/survey_finished.pt')
    def finished_survey_view(self):
        """ The thank-you screen
        """
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
            if not ISurveySection.providedBy(section):
                continue
            sections.append(section)
            section_results[section.__name__] = section.question_format_results()

        self.response['sections'] = sections
        self.response['section_results'] = section_results
        self.response['get_questions_for_section'] = self._get_questions
        return self.response

    def _get_questions(self, section):
        question_ids = list(section.question_ids)
        for part_data in section.responses.values():
            [question_ids.append(x) for x in part_data.keys() if x not in question_ids]
        return [section.question_object_from_id(id) for id in question_ids]

    @view_config(context = ISurveySection, renderer = 'templates/survey_form.pt', permission = security.VIEW)
    def show_dummy_form_view(self):
        schema = colander.Schema()
        self.context.append_questions_to_schema(schema, self.request)
        form = Form(schema)
        self.response['form_resources'] = form.get_widget_resources()
        self.response['dummy_form'] = form.render()
        return self.response

    @view_config(context = ITextSection, renderer = 'templates/survey_form.pt', permission = security.VIEW)
    def show_dummy_text_view(self):
        schema = createSchema(self.context.schemas['edit'])
        form = Form(schema)
        lang = self.get_lang()
        appstruct = {'title': self.context.get_title(lang = lang),
                     'description': self.context.get_description(lang = lang)}
        self.response['form_resources'] = form.get_widget_resources()
        self.response['dummy_form'] = form.render(readonly = True, appstruct = appstruct)
        return self.response

    def send_invitation(self, email):
        subject = self.localizer.translate(_(u"Invitation to survey '${s_title}'", mapping = {'s_title': self.context.title}))
        msg = _(u"self_added_invitation_text",
                default = u"You receive this email since someone (hopefully you) entered "
                u"your email address as a participant of this survey. Simply follow the link to participate in the survey. "
                u"In case you didn't ask for this email, or you've changed your mind about participating, simply do nothing. ")
        self.context.send_invitations(self.request, emails = [email],
                                      subject = subject, message = msg)
        msg = _(u"invitation_sent_notice",
                default = u"Invitation sent. Check your inbox in a few minutes. If it hasn't arrived within 15 minutes, check your spam folder.")
        self.add_flash_message(msg)

    @view_config(context = ISurvey, renderer = 'templates/survey_view.pt', permission = NO_PERMISSION_REQUIRED)
    def survey_view(self):
        if self.userid:
            return HTTPFound(location = self.request.resource_url(self.context, 'view'))
        try:
            self.context.check_open()
            self.response['survey_open'] = True
        except SurveyUnavailableError:
            self.response['survey_open'] = False
        self.response['allow_anonymous_to_participate'] = self.context.get_field_value('allow_anonymous_to_participate', False)
        if self.response['survey_open']:
            schema = createSchema('ParticipantControlsSchema')
            schema = schema.bind(context = self.context, request = self.request)            
            form = Form(schema, buttons=(self.buttons['send'],))
            self.response['form_resources'] = form.get_widget_resources()
            if 'send' in self.request.POST:
                controls = self.request.POST.items()
                try:
                    appstruct = form.validate(controls)
                except ValidationFailure, e:
                    self.response['form'] = e.render()
                    return self.response

                if appstruct['participant_actions'] == u"send_anon_invitation" and self.response['allow_anonymous_to_participate']:
                    self.send_invitation(appstruct['email'])

                if appstruct['participant_actions'] == u"start_anon" and self.context.get_field_value('allow_anonymous_to_start', False):
                    if appstruct['email'] in self.context.tickets.values():
                        #Check if participant actually started the survey, or was just invited
                        #FIXME: We're looping twice - we should use a reverse key registry instead.
                        for (participant_uid, email) in self.context.tickets.items():
                            #This will of course be true, since we already know email is in there.
                            if appstruct['email'] == email:
                                if self.root['participants'].participant_by_ids(self.context.__name__,  participant_uid):
                                    #Abort if survey data founds
                                    msg = _(u"email_already_used_notice",
                                            default = u"Your email address has already been used within this survey. "
                                                    u"If you need to change your replies, use the access link provided when you started "
                                                    u"the survey, or resend the link by using the form below.")
                                    self.add_flash_message(msg)
                                    return HTTPFound(location = self.request.resource_url(self.context))
                    invitation_uid = self.context.create_ticket(appstruct['email'])
                    access_link = self.request.resource_url(self.context, 'do', query = {'uid': invitation_uid})
                    msg = _(u"participant_unverified_link_notice",
                            default = u"Important! Since you're starting this survey without a verified email, please copy this "
                                    u"link in case you need to access the survey again: ${link}",
                            mapping = {'link': access_link})
                    self.add_flash_message(msg)
                    return HTTPFound(location = access_link)

                if appstruct['participant_actions'] == u"resend_access":
                    if appstruct['email'] not in self.context.tickets.values() and not self.response['allow_anonymous_to_participate']:
                        msg = _(u"cant_resend_access_error",
                                default = u"Unable to resend access code - your email wasn't found among the invited.")
                        self.add_flash_message(msg)
                        return HTTPFound(location = self.request.resource_url(self.context))
                    self.send_invitation(appstruct['email'])

            self.response['form'] = form.render()
        return self.response

    @view_config(name = 'view', context=ISurvey, renderer='templates/survey_admin_view.pt', permission=security.VIEW)
    def survey_admin_view(self):
        start_time = self.context.get_field_value('start_time', None)
        end_time = self.context.get_field_value('end_time', None)
        if start_time:
            start_time = self.user_dt.dt_format(start_time)
        if end_time:
            end_time = self.user_dt.dt_format(end_time)
        self.response['start_time'] = start_time
        self.response['end_time'] = end_time
        #Is survey active?
        try:
            self.context.check_open()
            msg = _(u"The survey is currently open.")
        except SurveyUnavailableError as e:
            msg = e.msg
        self.response['survey_state_msg'] = msg
        return self.response

    @view_config(name='reorder', context=IChoiceQuestionType, renderer='templates/reorder_folder.pt', permission=security.EDIT)
    @view_config(name='reorder', context=IMultiChoiceQuestionType, renderer='templates/reorder_folder.pt', permission=security.EDIT)
    @view_config(name='reorder', context=ISurvey, renderer='templates/reorder_folder.pt', permission=security.EDIT)
    def reorder_folder(self):
        post = self.request.POST
        ui_sortable.need()
        if 'cancel' in self.request.POST:
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)
        if 'save' in post:
            controls = self.request.POST.items()
            items = []
            for (k, v) in controls:
                if k == 'items':
                    items.append(v)
            self.context.order = items
            self.add_flash_message(_('Order updated'))
        form = Form(colander.Schema())
        self.response['form_resources'] = form.get_widget_resources()
        self.response['dummy_form'] = form.render()
        return self.response

    def process_question_ids(self, survey):
        sect_id_questions = self.request.POST.dict_of_lists()
        for section in survey.values():
            if ISurveySection.providedBy(section):
                sect_id_questions.setdefault(section.__name__, [])
        for (sect_id, question_ids) in sect_id_questions.items():
            if sect_id in survey: #Might be other things than section ids within the post
                survey[sect_id].set_question_ids(question_ids)

    @view_config(name='manage_questions', context=ISurvey, renderer='templates/manage_questions.pt', permission=security.EDIT)
    def manage_questions(self):
        manage_questions.need()
        post = self.request.POST
        if 'cancel' in self.request.POST:
            url = self.request.resource_url(self.context)
            return HTTPFound(location = url)
        if 'save' in post:
            self.process_question_ids(self.context)
            self.add_flash_message(_('Updated'))

        self.response['organisation'] = org = find_interface(self.context, IOrganisation)

        picked_questions = set()
        survey_sections = []
        for section in self.context.values():
            if not ISurveySection.providedBy(section):
                continue
            picked_questions.update(section.question_ids)
            survey_sections.append(section)
        self.response['survey_sections'] = survey_sections
        if not survey_sections:
            msg = _(u"no_sections_added_notice",
                    default = u"You need to add survey sections and then use this view to manage the questions.")
            self.add_flash_message(msg)
        #Load all question objects that haven't been picked
        questions = org.questions
        self.response['available_questions'] = [questions[x] for x in questions if x not in picked_questions]
        return self.response
        
    @view_config(name='export.csv', context=ISurvey, permission=security.VIEW)
    def export(self):
        """ Results screen
        """
        output = StringIO.StringIO()
        writer = csv.writer(output, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow([self.context.title.encode('utf-8')])
        languages = self.context.get_language_participants
        lrow = [_(u"Languages").encode('utf-8'), _(u"Total").encode('utf-8')]
        langs = set(languages.keys()) | set(self.context.get_available_languages())
        for lang in langs:
            lrow.append("%s (%s)" % (self.trans_util.title_for_code(lang).encode('utf-8'), self.trans_util.title_for_code_default(lang).encode('utf-8')))
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

        for section in self.context.values():
            if not ISurveySection.providedBy(section):
                continue
            writer.writerow([])
            writer.writerow(['Section: %s' % section.title.encode('utf-8')])
            writer.writerow([])

            #Sort all questions according to which type they are
            results = {}
            errors = 0
            for question in self._get_questions(section):
                if question is None:
                    errors += 1
                    continue
                q_type = question.get_question_type()
                if q_type not in results:
                    results[q_type] = dict(
                        obj = question.get_type_object(),
                        questions = [],
                     )
                results[q_type]['questions'].append(question)
            if errors:
                msg = _(u"unexportable_response_data_due_to_missing_question ",
                        default = _(u"Export encountered problem(s). "
                                    u"The response information contain data that can't be linked to any question. "
                                    u"They were probably deleted after the completion of the survey. This happend ${count} time(s)."),
                        mapping = {'count': errors})
                self.add_flash_message(msg)
            #Loop trough all sorted questions
            for type_questions in results.values():
                writer.writerow(type_questions['obj'].csv_header())
                for question in type_questions['questions']:
                    title = question.get_title().encode('utf-8')
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
class CloneSurveyForm(BaseForm):

    @property
    def buttons(self):
        return (self.button_save, self.button_cancel,)

    @reify
    def schema(self):
        return createSchema(self.context.schemas['clone'])

    def appstruct(self):
        appstruct = {}
        appstruct['title'] = self.localizer.translate(_(u"${title} (Clone)", mapping = {'title': self.context.title}))
        return appstruct

    def save_success(self, appstruct):
        new_survey = self.context.clone(appstruct['title'], appstruct['destination'])
        url = self.request.resource_url(new_survey, 'edit')
        return HTTPFound(location = url)


@view_config(name='invitation_emails', context=ISurvey, renderer=BASE_FORM_TEMPLATE, permission=security.MANAGE_SURVEY)
class InvitationEmailsForm(BaseForm):

    def __call__(self):
        return_url = self.request.resource_url(self.context)
        try:
            self.context.check_open()
        except SurveyUnavailableError as exc:
            self.add_flash_message(exc.msg)
            return HTTPFound(location = return_url)
        survey_sections = [x for x in self.context.values() if ISurveySection.providedBy(x)]
        question_count = sum([len(x.question_ids) for x in survey_sections])
        if not question_count:
            msg = _(u"no_questions_notice",
                    default = u"There aren't any questions yet. You need to add survey sections and questions, "
                              u"otherwise invited users won't be able to do anything.")
            self.add_flash_message(msg)
            return HTTPFound(location = return_url)
        return super(InvitationEmailsForm, self).__call__()

    @property
    def buttons(self):
        return (self.button_send, self.button_cancel,)

    @reify
    def schema(self):
        return createSchema(self.context.schemas['invitation'])

    def send_success(self, appstruct):
        emails = set()
        for email in appstruct['emails'].splitlines():
            emails.add(email.strip())
        message = appstruct['message']
        subject = appstruct['subject']
        self.context.send_invitations(self.request, emails, subject, message)
        msg = _(u"invitations_sent_notice",
                default = u"${count} Invitation(s) sent",
                mapping = {'count': len(emails)})
        self.add_flash_message(msg)
        url = self.request.resource_url(self.context)
        return HTTPFound(location = url)
