import unittest

from pyramid import testing
from zope.interface.verify import verifyObject


class ParticipantTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.participants import Participant
        return Participant()
    
    def test_interface(self):
        from madetomeasure.interfaces import IParticipant
        obj = self._make_obj()
        self.assertTrue(verifyObject(IParticipant, obj))

    