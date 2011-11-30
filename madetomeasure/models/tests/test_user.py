import unittest
from datetime import timedelta
from datetime import datetime

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
        
    def test_get_title(self):
        user = self._cut()
        fname = 'Kalle'
        lname = 'Karlsson'
        user.set_field_value('first_name', fname)
        user.set_field_value('last_name', lname)
        self.assertEqual(user.get_title(), "%s %s" % (fname, lname))
        
    def test_check_password(self):
        self.config.scan('betahaus.pyracont.fields.password')
        user = self._cut()
        password = 'password1'
        user.set_field_value('password', password)
        self.assertTrue(user.check_password(password))
        
    def test_new_request_password_token(self):
        user = self._cut()
        user.set_field_value('email', 'test@test.com')
        request = testing.DummyRequest()
        self.config.include('pyramid_mailer.testing')
        user.new_request_password_token(request)
        self.failUnless(user.__token__())
        
    def test_remove_password_token(self):
        user = self._cut()
        user.__token__ = object()
        user.remove_password_token()
        self.assertIsNone(user.__token__)

#FIXME:
#All other accessors / mutators

class RequestPasswordTokenTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
    
    def _make_obj(self):
        from madetomeasure.models.users import RequestPasswordToken
        return RequestPasswordToken()

    def test_initial_values(self):
        obj = self._make_obj()
        self.assertEqual(obj.created + timedelta(days=3), obj.expires)

    def test_call_returns_token(self):
        obj = self._make_obj()
        self.assertEqual(obj(), obj.token)
        self.assertEqual(len(obj()), 30)
    
    def test_validate_works(self):
        obj = self._make_obj()
        obj.token = 'dummy'
        obj.validate('dummy')
    
    def test_validate_expired(self):
        obj = self._make_obj()
        obj.token = 'dummy'
        obj.expires = datetime.utcnow() - timedelta(days=1)
        self.assertRaises(ValueError, obj.validate, 'dummy')

    def test_validate_wrong_token(self):
        obj = self._make_obj()
        obj.token = 'dummy'
        self.assertRaises(ValueError, obj.validate, 'wrong')
