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

    def _add_users(self, users):
        from madetomeasure.models.users import User
        for u in ('kalle', 'olle', 'stina', 'lisa'):
            user = User()
            user.set_field_value('email', u+'@test.com')
            users[u] = user

    def test_verify_class(self):
        self.failUnless(verifyClass(IUsers, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IUsers, self._cut()))
        
    def test_get_user_by_email(self):
        users = self._cut()
        self._add_users(users)
        self.assertIsNotNone(users.get_user_by_email('olle@test.com'))
        

#FIXME:
#All other accessors / mutators
