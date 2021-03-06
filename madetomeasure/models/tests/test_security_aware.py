import unittest

from pyramid import testing


class SecurityAwareTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        """ Security aware is a mixin class, so we need to add BaseFolder too"""
        from madetomeasure.models.security_aware import SecurityAware
        from betahaus.pyracont import BaseFolder
        
        class DummyContent(BaseFolder, SecurityAware):
            pass
        
        return DummyContent()

    def test_verify_object(self):
        from zope.interface.verify import verifyObject
        from madetomeasure.interfaces import ISecurityAware
        obj = self._make_obj()
        self.assertTrue(verifyObject(ISecurityAware, obj))

    def test_get_groups(self):
        obj = self._make_obj()
        self.assertEqual(obj.get_groups('User 404'), ())
        obj.add_groups('tester', ['group:Hipsters'])
        self.assertEqual(obj.get_groups('tester'), ('group:Hipsters',))

    def test_add_groups(self):
        obj = self._make_obj()
        obj.add_groups('tester', ['group:Hipsters'])
        self.assertEqual(obj.get_groups('tester'), ('group:Hipsters',))
        obj.add_groups('tester', ('role:Admin',))
        self.assertEqual(obj.get_groups('tester'), ('group:Hipsters', 'role:Admin',))

    def test_set_groups(self):
        obj = self._make_obj()
        obj.set_groups('tester', ['group:Hipsters'])
        self.assertEqual(obj.get_groups('tester'), ('group:Hipsters',))
        obj.set_groups('tester', ('role:Admin',))
        self.assertEqual(obj.get_groups('tester'), ('role:Admin',))

    def test_add_bad_group(self):
        obj = self._make_obj()
        self.assertRaises(ValueError, obj.add_groups, 'tester', ['Hipsters'])

    def test_get_security(self):
        from madetomeasure.models.app import bootstrap_root
        self.config.scan('betahaus.pyracont.fields.password')
        obj = bootstrap_root()
        self.assertEqual(obj.get_security(), [{'userid': 'admin', 'groups': ('role:Admin',)}])
        obj.set_groups('admin', ['role:Admin', 'group:Hipsters'])
        self.assertEqual(obj.get_security(), [{'userid': 'admin', 'groups': ('group:Hipsters', 'role:Admin')}])

    def test_update_userids_permissions(self):
        obj = self._make_obj()
        obj.update_userids_permissions([{'userid': 'robin', 'groups': ('group:DeathCab', 'role:Moderator')}])
        self.assertEqual(obj._groups['robin'], ('group:DeathCab', 'role:Moderator'))

    def test_list_all_groups(self):
        obj = self._make_obj()
        obj.add_groups('tester1', ['group:Hipsters'])
        obj.add_groups('tester2', ['role:Confused', 'group:Hipsters'])
        obj.add_groups('tester3', ['role:Confused', 'group:PeterLicht'])
        self.assertEqual(obj.list_all_groups(), set(('group:Hipsters', 'role:Confused', 'group:PeterLicht')) )
