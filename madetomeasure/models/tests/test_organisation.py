import unittest

from pyramid import testing
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Authenticated
from zope.interface.verify import verifyObject
from zope.interface.verify import verifyClass

from madetomeasure import security
from madetomeasure.interfaces import IOrganisation
from madetomeasure.models.app import bootstrap_root


admin = set([security.ROLE_ADMIN])
organisation_manager = set([security.ROLE_ORGANISATION_MANAGER])
translator = set([security.ROLE_TRANSLATOR])


class OrganisationTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.organisation import Organisation
        return Organisation

    def test_verify_class(self):
        self.failUnless(verifyClass(IOrganisation, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IOrganisation, self._cut()))

    def test_variants(self):
        obj = self._cut()
        self.assertEqual(len(obj.variants), 0)
        question_name = 'q1'
        lang = 'sv'
        value = 'Testing variants'
        obj.set_variant(question_name, lang, value)
        self.assertEqual(obj.get_variant(question_name, lang), value)
        self.assertEqual(obj.get_variant('q2', lang), None)
        self.assertEqual(obj.get_variant(question_name, 'ru'), None)
        self.assertEqual(obj.get_variant('q2', 'ru'), None)

    def test_questions(self):
        from madetomeasure.models.questions import Question
        self.config.scan('betahaus.pyracont.fields.password')
        root = bootstrap_root()
        root['o'] = obj = self._cut()
        obj['questions']['q1'] = Question()
        root['questions']['q2'] = Question()
        self.assertEqual(obj.questions.keys(), [u'q1', u'q2'])


#Test schema and expected usage
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

