import colander
import deform
from betahaus.pyracont.decorators import schema_factory

from madetomeasure import MadeToMeasureTSF as _


@schema_factory('EditSiteRoot')
class EditSiteRoot(colander.Schema):
    footer_html = colander.SchemaNode(colander.String(),
                                 title = _(u"Footer HTML code"),
                                 missing=u"",
                                 widget=deform.widget.RichTextWidget(rows=10, cols=50))
