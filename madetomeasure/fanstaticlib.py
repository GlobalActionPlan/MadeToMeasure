from fanstatic import (Library,
                       Resource,
                       Group)
from js.deform import (deform_basic,
                       resource_mapping)
from js.jqueryui import ui_sortable
from js.deform_bootstrap import deform_bootstrap_js
from js.bootstrap import bootstrap

#Patch resource mapping to fetch deform basics instead of beautify.css
#resource_mapping['deform'] = [deform_basic,]

m2m_lib = Library('m2m_lib', 'static')

#reset_css = Resource(m2m_lib, 'reset.css') reset_css
main_css = Resource(m2m_lib, 'main.css', depends = (deform_basic, bootstrap,))

main_js = Resource(m2m_lib, 'main.js', depends = (bootstrap, deform_bootstrap_js,))
manage_questions = Resource(m2m_lib, 'manage_questions.js', depends = (main_js, ui_sortable,))

survey_managers_resources = Group([main_css, main_js])
survey_participants_resources = Group([main_css, main_js])
#FIXME: Auto_need currently fetched beautify.css from deform. We might need to override that.
