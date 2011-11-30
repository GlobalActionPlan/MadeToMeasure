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
