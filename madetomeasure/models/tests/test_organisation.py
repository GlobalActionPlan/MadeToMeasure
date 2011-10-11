import unittest

from pyramid import testing
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Authenticated
from zope.interface.verify import verifyObject

from madetomeasure import security


admin = set([security.ROLE_ADMIN])
organisation_manager = set([security.ROLE_ORGANISATION_MANAGER])


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


class OrganisationPermissionTests(unittest.TestCase):
    """ Check permissions. """

    def setUp(self):
        self.config = testing.setUp()
        policy = ACLAuthorizationPolicy()
        self.pap = policy.principals_allowed_by_permission

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.organisation import Organisation
        return Organisation()
        
    def test_permissions(self):
        obj = self._make_obj()
        
        # VIEW
        self.assertEqual(self.pap(obj, security.VIEW), admin | organisation_manager)
        
        # EDIT
        self.assertEqual(self.pap(obj, security.EDIT), admin | organisation_manager)

        # DELETE
        self.assertEqual(self.pap(obj, security.EDIT), admin | organisation_manager)

        # TRANSLATE
        self.assertEqual(self.pap(obj, security.TRANSLATE), admin | organisation_manager)

        # MANAGE_SURVEY
        self.assertEqual(self.pap(obj, security.MANAGE_SURVEY), admin | organisation_manager)

        # ADD_QUESTION
        self.assertEqual(self.pap(obj, security.ADD_QUESTION), admin | organisation_manager)

        # ADD_SURVEY
        self.assertEqual(self.pap(obj, security.ADD_SURVEY), admin | organisation_manager)

        # ADD_SURVEY_SECTION
        self.assertEqual(self.pap(obj, security.ADD_SURVEY_SECTION), admin | organisation_manager)

    def test_invariants(self):
        obj = self._make_obj()
        self.assertEqual(len(obj.invariants), 0)
        
        question_uid = 'q1'
        lang = 'sv'
        value = 'Testing invariants'
        
        obj.set_invariant(question_uid, lang, value)
        self.assertEqual(obj.get_invariant(question_uid, lang), value)
        
        self.assertEqual(obj.get_invariant('q2', lang), None)
        self.assertEqual(obj.get_invariant(question_uid, 'ru'), None)
        self.assertEqual(obj.get_invariant('q2', 'ru'), None)
