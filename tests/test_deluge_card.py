# test_module.py
import importlib.metadata
import os
from pathlib import Path
from unittest import TestCase

from deluge_card import DelugeCardFS


class TestPackage(TestCase):
    def test_has_version_attribute(self):
        ver = importlib.metadata.version('deluge-card')
        self.assertTrue(ver)


class TestListSongs(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_list_all_songs(self):
        songs = list(self.card.songs())
        self.assertEqual(len(songs), 3)

    def test_list_sampless_0(self):
        songs = list(self.card.songs("*002*"))
        self.assertEqual(len(songs), 2)

    def test_list_songs_1(self):
        songs = list(self.card.songs("**/SONG002*"))
        self.assertEqual(len(songs), 2)

    def test_list_songs_2(self):
        songs = list(self.card.songs("**/DC01/**/SONG002A*"))
        self.assertEqual(len(songs), 1)

    def test_list_songs_3(self):
        songs = list(self.card.songs("**/DC01/**/SONG???A*"))
        self.assertEqual(len(songs), 1)


class TestListSamples(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_list_all_samples(self):
        samples = list(self.card.samples())
        self.assertEqual(len(samples), 3)

    def test_list_samples_0(self):
        samples = list(self.card.samples("*snare*"))
        self.assertEqual(len(samples), 1)

    def test_list_samples_1(self):
        samples = list(self.card.samples("**/Artists/A/*"))
        self.assertEqual(len(samples), 3)

    def test_list_samples_2(self):
        samples = list(self.card.samples("**/Artists/A/kick*"))
        self.assertEqual(len(samples), 1)
