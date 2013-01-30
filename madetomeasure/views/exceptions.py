from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import ISettings

from madetomeasure import MadeToMeasureTSF as _


class ExceptionsView(object):

    def __init__(self, exception, request):
        self.exception = exception
        self.request = request
        self.response = {}

    @view_config(context=HTTPForbidden)
    def forbidden_view(self):
        settings = self.request.registry.getUtility(ISettings)
        if settings.get('debug_templates', False):
            raise self.exception
        else:
            return HTTPFound(location = "/login")

    @view_config(context=HTTPNotFound, renderer="templates/exceptions.pt")
    def not_found_view(self):
        #FIXME: Write a proper 404 page
        self.response['msg'] = _(u"not_found_error_text",
                                 u"Couldn't find that page.")
        return self.response
