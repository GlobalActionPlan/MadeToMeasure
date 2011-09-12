from pyramid.view import view_config
from madetomeasure.models import MyModel

@view_config(context=MyModel, renderer='madetomeasure:templates/mytemplate.pt')
def my_view(request):
    return {'project':'MadeToMeasure'}
