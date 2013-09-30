import colander
from unittest import TestCase

from pyramid import testing


class MultipleEmailValidatorTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _fut(self):
        from madetomeasure.schemas.validators import multiple_email_validator
        return multiple_email_validator

    def test_single(self):
        self.assertEqual(self._fut(None, "one@two.com"), None)

    def test_single_w_bad_chars(self):
        self.assertRaises(colander.Invalid, self._fut, None, "\none@two.com hello! \n")

    def test_multiple_good(self):
        self.assertEqual(self._fut(None, "one@two.com\nthree@four.net\nfive@six.com"), None)

    def test_multiple_one_bad(self):
        self.assertRaises(colander.Invalid, self._fut, None, "one@two.com\nthree@four.net\nfive@six.com\none@two.com hello! \n")


class PasswordValidationTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _fut(self):
        from madetomeasure.schemas.users import password_validation
        return password_validation

    def test_good(self):
        self.assertEqual(self._fut(None, "password"), None)

    def test_short(self):
        self.assertRaises(colander.Invalid, self._fut, None, "passw")

    def test_long(self):
        password = "".join(["1"]*101)
        self.assertRaises(colander.Invalid, self._fut, None, password)


class OrganisationValidator(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def dummy_node(self):
        return colander.SchemaNode(colander.String())

    @property
    def _fut(self):
        from madetomeasure.models.root import SiteRoot
        root = SiteRoot()
        from madetomeasure.models.organisation import Organisation
        organisation = Organisation()
        organisation.set_field_value('title', 'O1')
        root['o1'] = organisation
        from madetomeasure.models.questions import Question
        question = Question()
        question.set_field_value('title', 'Q1')
        root['q1'] = question
        from madetomeasure.schemas.surveys import OrganisationValidator
        organisation_validator = OrganisationValidator(context = organisation, request = testing.DummyRequest())
        return organisation_validator

    def test_valid(self):
        self.assertEqual(self._fut(self.dummy_node, "o1"), None)
        
    def test_not_organisation(self):
        self.assertRaises(colander.Invalid, self._fut, self.dummy_node, "q1")
        
    def test_missing(self):
        self.assertRaises(colander.Invalid, self._fut, self.dummy_node, "")
        
    #FIXME: do thest with proper permissionsystem


class ConfirmDeleteWithTitleValidatorTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.schemas.validators import ConfirmDeleteWithTitleValidator
        return ConfirmDeleteWithTitleValidator

    def test_correct_title(self):
        context = testing.DummyModel()
        context.title = u"One title"
        obj = self._cut(context)
        self.assertEqual(obj(None, u"One title"), None)

    def test_wrong_title(self):
        context = testing.DummyModel()
        context.title = u"One title"
        obj = self._cut(context)
        self.assertRaises(colander.Invalid, obj, None, "other title")
