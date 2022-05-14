import itertools
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


class TestSynthSamples(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_find_all_synth_samples(self):
        synth_samples = itertools.chain.from_iterable(map(lambda synth: synth.samples(), self.card.synths()))
        ksl = list(synth_samples)
        print(ksl)
        self.assertEqual(len(ksl), 1)  # 1 in 1 synth

    def test_find_synth_hihat_samples(self):
        pattern = '**/DX7/*.wav'
        synth_samples = itertools.chain.from_iterable(map(lambda synth: synth.samples(pattern), self.card.synths()))
        ksl = list(synth_samples)
        print(ksl)
        self.assertEqual(len(ksl), 1)
