from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound

from madetomeasure import MadeToMeasureTSF as _
from madetomeasure.views.base import BaseView

class ExceptionsView(BaseView):

    @view_config(context = HTTPForbidden, renderer="templates/exceptions.pt")
    def forbidden_view(self):
        if self.userid:
            msg = _(u"not_allowed_error_txt",
                    default = u"You did something that the server didn't allow. (Error 403)")
        else:
            msg = _(u"not_allowed_error_anon_txt",
                    default = u"You did something that the server didn't allow. If you are a manager, perhaps you need to log in? (Error 403)")
        self.response['msg'] = msg
        return self.response

    @view_config(context = HTTPNotFound, renderer="templates/exceptions.pt")
    def not_found_view(self):
        self.response['msg'] = _(u"not_found_error_text",
                                 default = u"Couldn't find anything with this URL. (Error 404)")
        return self.response
