import unittest

from pyramid import testing
from zope.interface.verify import verifyObject


class OrganisationTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.organisation import Organisation
        return Organisation()
    
    def test_interface(self):
        from madetomeasure.interfaces import IOrganisation
        obj = self._make_obj()
        self.assertTrue(verifyObject(IOrganisation, obj))
