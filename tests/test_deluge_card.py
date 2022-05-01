# test_module.py

import importlib.metadata
from unittest import TestCase


class TestPackage(TestCase):
    def test_has_version_attribute(self):
        ver = importlib.metadata.version('deluge-card')
        self.assertTrue(ver)
