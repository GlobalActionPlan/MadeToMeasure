""" Contains things that should be loaded on startup.
    This patches deform to use pyramids translator.
"""

import os
from pkg_resources import resource_filename

from deform import Form
from pyramid.i18n import get_locale_name
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request


def translator(term):
    return get_localizer(get_current_request()).translate(term)

#Activate code below if we override deform widgets in views/templates/widgets
CURRENT_PATH = resource_filename('madetomeasure', '')
search_path = (os.path.join(CURRENT_PATH, 'views', 'templates', 'widgets'),
               resource_filename('deform', 'templates'))

Form.set_zpt_renderer(search_path, translator=translator)
