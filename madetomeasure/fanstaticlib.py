from fanstatic import (Library,
                       Resource,
                       Group)
from js.jqueryui import ui_sortable
from js.bootstrap import (bootstrap_theme,)


m2m_lib = Library('m2m_lib', 'static')

main_css = Resource(m2m_lib, 'main.css', depends = (bootstrap_theme,))

main_js = Resource(m2m_lib, 'main.js')
manage_questions = Resource(m2m_lib, 'manage_questions.js', depends = (main_js, ui_sortable,)) #FIXME
questions_listing = Resource(m2m_lib, 'questions_listing.js', depends = (main_js,))

survey_managers_resources = Group([main_css, main_js])
survey_participants_resources = Group([main_css, main_js])
