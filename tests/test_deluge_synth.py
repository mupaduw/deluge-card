import os
from pathlib import Path
from unittest import TestCase, mock

from lxml import etree

from deluge_card import DelugeCardFS


class TestListSynths(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_read_synth_fixture(self):
        sf = Path(self.card.card_root, 'SYNTHS', 'SYNT991A.XML')
        with self.assertRaises(Exception) as ctx:
            tree = etree.parse(sf)
