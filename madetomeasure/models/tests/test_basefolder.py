import unittest

import colander
from pyramid import testing


class BaseFolderTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _make_obj(self):
        from madetomeasure.models.base import BaseFolder
        return BaseFolder()
    
    def test_title(self):
        obj = self._make_obj()
        self.assertEqual(obj.get_title(), u'')
        
        obj.set_title(u"Hello world")
        self.assertEqual(obj.get_title(), u"Hello world")
