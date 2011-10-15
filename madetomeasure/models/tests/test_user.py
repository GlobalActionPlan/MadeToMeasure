import unittest

from pyramid import testing
from zope.interface.verify import verifyObject
from zope.interface.verify import verifyClass

from madetomeasure.interfaces import IUser


class UserTests(unittest.TestCase):
    """ User model tests. """

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.users import User
        return User

    def test_verify_class(self):
        self.failUnless(verifyClass(IUser, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IUser, self._cut()))

#FIXME:
#test title = first + last name
#All other accessors / mutators