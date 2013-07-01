import unittest

from pyramid import testing
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Authenticated
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from madetomeasure import security
from madetomeasure.interfaces import ISiteRoot


admin = set([security.ROLE_ADMIN])
translator = set([security.ROLE_TRANSLATOR])
auth = set([Authenticated])


class RootPermissionTests(unittest.TestCase):
    """ Check permissions. """

    def setUp(self):
        self.config = testing.setUp()
        policy = ACLAuthorizationPolicy()
        self.pap = policy.principals_allowed_by_permission

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.root import SiteRoot
        return SiteRoot

    def test_verify_class(self):
        self.failUnless(verifyClass(ISiteRoot, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(ISiteRoot, self._cut()))

    def test_permissions(self):
        obj = self._cut()
        self.assertEqual(self.pap(obj, security.VIEW), admin | auth)
        self.assertEqual(self.pap(obj, security.EDIT), admin)
        self.assertEqual(self.pap(obj, security.EDIT), admin)
        self.assertEqual(self.pap(obj, security.TRANSLATE), admin)
        self.assertEqual(self.pap(obj, security.MANAGE_SURVEY), admin)
        self.assertEqual(self.pap(obj, security.ADD_QUESTION), admin)
        self.assertEqual(self.pap(obj, security.ADD_SURVEY), admin)
        self.assertEqual(self.pap(obj, security.ADD_SURVEY_SECTION), admin)
        self.assertEqual(self.pap(obj, security.ADD_USER), admin)
        self.assertEqual(self.pap(obj, security.ADD_ORGANISATION), admin)
