# test_module.py

import importlib.metadata
from unittest import TestCase


class TestModule(TestCase):
    def test_has_version_attribute(self):
        ver = importlib.metadata.version('deluge_card')
        self.assertTrue(ver)
