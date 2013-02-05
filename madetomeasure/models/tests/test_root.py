import unittest

from pyramid import testing
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Authenticated
from zope.interface.verify import verifyObject

from madetomeasure import security


admin = set([security.ROLE_ADMIN])
translator = set([security.ROLE_TRANSLATOR])


class RootPermissionTests(unittest.TestCase):
    """ Check permissions. """

    def setUp(self):
        self.config = testing.setUp()
        policy = ACLAuthorizationPolicy()
        self.pap = policy.principals_allowed_by_permission

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.root import SiteRoot
        return SiteRoot()
        
    def test_permissions(self):
        obj = self._make_obj()
        
        # VIEW
        self.assertEqual(self.pap(obj, security.VIEW), admin | translator)
        
        # EDIT
        self.assertEqual(self.pap(obj, security.EDIT), admin)

        # DELETE
        self.assertEqual(self.pap(obj, security.EDIT), admin)

        # TRANSLATE
        self.assertEqual(self.pap(obj, security.TRANSLATE), admin)

        # MANAGE_SURVEY
        self.assertEqual(self.pap(obj, security.MANAGE_SURVEY), admin)

        # ADD_QUESTION
        self.assertEqual(self.pap(obj, security.ADD_QUESTION), admin)

        # ADD_SURVEY
        self.assertEqual(self.pap(obj, security.ADD_SURVEY), admin)

        # ADD_SURVEY_SECTION
        self.assertEqual(self.pap(obj, security.ADD_SURVEY_SECTION), admin)

        # ADD_USER
        self.assertEqual(self.pap(obj, security.ADD_USER), admin)

        # ADD_ORGANISATION
        self.assertEqual(self.pap(obj, security.ADD_ORGANISATION), admin)
