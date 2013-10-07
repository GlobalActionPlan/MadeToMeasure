# -*- coding: utf-8 -*-

import unittest

from pyramid import testing
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject

from madetomeasure.interfaces import IQuestions


class QuestionsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.questions import Questions
        return Questions

    def test_verify_class(self):
        self.failUnless(verifyClass(IQuestions, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IQuestions, self._cut()))


class LocalQuestionsTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from madetomeasure.models.questions import LocalQuestions
        return LocalQuestions

    def test_verify_class(self):
        self.failUnless(verifyClass(IQuestions, self._cut))

    def test_verify_obj(self):
        self.failUnless(verifyObject(IQuestions, self._cut()))
