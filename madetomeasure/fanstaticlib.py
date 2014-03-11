from fanstatic import (Library,
                       Resource,
                       Group)
from js.deform import (deform_basic,
                       resource_mapping)

#Patch resource mapping to fetch deform basics instead of beautify.css
resource_mapping['deform'] = [deform_basic,]

m2m_lib = Library('m2m_lib', 'static')

reset_css = Resource(m2m_lib, 'reset.css')
main_css = Resource(m2m_lib, 'main.css', depends = (reset_css, deform_basic,))


survey_managers_resources = Group([main_css])
survey_participants_resources = Group([main_css])
#FIXME: Auto_need currently fetched beautify.css from deform. We might need to override that.
