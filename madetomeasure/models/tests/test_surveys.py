# -*- coding: utf-8 -*-

import unittest

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from madetomeasure.interfaces import ISurveys


class SurveysTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.surveys import Surveys
        return Surveys

    def test_verify_class(self):
        self.failUnless(verifyClass(ISurveys, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(ISurveys, self._cut()))
