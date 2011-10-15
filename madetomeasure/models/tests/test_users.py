import unittest

from pyramid import testing
from zope.interface.verify import verifyObject
from zope.interface.verify import verifyClass

from madetomeasure.interfaces import IUsers


class UsersTests(unittest.TestCase):
    """ Users model tests. """

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.users import Users
        return Users

    def test_verify_class(self):
        self.failUnless(verifyClass(IUsers, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IUsers, self._cut()))

#FIXME:
#All other accessors / mutators