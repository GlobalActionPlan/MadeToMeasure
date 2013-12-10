import colander
from unittest import TestCase

from pyramid import testing

from madetomeasure.models.app import bootstrap_root


class OrganisationValidator(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.schemas.surveys import OrganisationValidator
        return OrganisationValidator

    def _fixture(self):
        self.config.include('madetomeasure')
        root = bootstrap_root()
        from madetomeasure.models.organisation import Organisation
        from madetomeasure.views.base import BaseView
        root['org'] = Organisation(title = 'Hello org')
        return BaseView(root, testing.DummyRequest())

    def _dummy_node(self):
        return colander.SchemaNode(colander.String(),
                                   name = 'hello')

    def test_correct_org(self):
        self.config.testing_securitypolicy('dummy', permissive = True)
        view = self._fixture()
        obj = self._cut(view)
        self.assertFalse(obj(self._dummy_node(), 'org'))

    def test_bad_name(self):
        self.config.testing_securitypolicy('dummy', permissive = True)
        view = self._fixture()
        obj = self._cut(view)
        self.assertRaises(colander.Invalid, obj, self._dummy_node(), '404')

    def test_bad_perm(self):
        self.config.testing_securitypolicy('dummy', permissive = False)
        view = self._fixture()
        obj = self._cut(view)
        self.assertRaises(colander.Invalid, obj, self._dummy_node(), 'org')

#FIXME: Proper permission test