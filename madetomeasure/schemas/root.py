import colander
import deform

from madetomeasure import MadeToMeasureTSF as _


class EditSiteRoot(colander.Schema):
    footer_html = colander.SchemaNode(colander.String(),
                                 title = _(u"Footer HTML code"),
                                 missing=u"",
                                 widget=deform.widget.TextAreaWidget(rows=10, cols=50))