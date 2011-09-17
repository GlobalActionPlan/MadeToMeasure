import unittest

import colander
from pyramid import testing
from zope.interface.verify import verifyObject
from BTrees.OOBTree import OOBTree


class SurveyTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models import Survey
        return Survey()
    
    def test_interface(self):
        from madetomeasure.interfaces import ISurvey
        obj = self._make_obj()
        self.assertTrue(verifyObject(ISurvey, obj))

    def test_invitation_emails(self):
        obj = self._make_obj()
        emails_field = "robin@betahaus.net\nfredrik@betahaus.net"
        obj.set_invitation_emails(emails_field)
        self.assertEqual(obj.get_invitation_emails(), emails_field)
    
    def test_from_address(self):
        obj = self._make_obj()
        email_field = "noreply@betahaus.net"
        obj.set_from_address(email_field)
        self.assertEqual(obj.get_from_address(), email_field)
    
    def test_mail_message(self):
        obj = self._make_obj()
        value = "Important message"
        obj.set_mail_message(value)
        self.assertEqual(obj.get_mail_message(), value)

    def test_finished_text(self):
        obj = self._make_obj()
        value = "We so happy now, okay?"
        obj.set_finished_text(value)
        self.assertEqual(obj.get_finished_text(), value)
