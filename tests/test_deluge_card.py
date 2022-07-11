# test_module.py
import importlib.metadata
import os
from pathlib import Path
from unittest import TestCase, mock

from deluge_card import DelugeCardFS


class TestPackage(TestCase):
    def test_has_version_attribute(self):
        ver = importlib.metadata.version('deluge-card')
        self.assertTrue(ver)


class TestListKits(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_list_all_kits(self):
        kits = list(self.card.kits())
        self.assertEqual(len(kits), 1)

    def test_list_filtered_kits(self):
        kits = list(self.card.kits("*014*"))
        self.assertEqual(len(kits), 1)


class TestListSynths(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_list_all_synths(self):
        synths = list(self.card.synths())
        self.assertEqual(len(synths), 3)

    def test_list_filtered_synths(self):
        synths = list(self.card.synths("*991A*"))
        self.assertEqual(len(synths), 1)


class TestListSongs(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_list_all_songs(self):
        songs = list(self.card.songs())
        self.assertEqual(len(songs), 6)

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
        for s in samples:
            print(
                s.path,
            )
            for st in s.settings:
                print(st.xml_file.path.name, st.xml_path)
        self.assertEqual(len(samples), 7)

    def test_list_samples_0(self):
        samples = list(self.card.samples("*snare*"))
        self.assertEqual(len(samples), 1)

    def test_list_samples_1(self):
        samples = list(self.card.samples("**/Artists/A/*"))
        self.assertEqual(len(samples), 3)

    def test_list_samples_2(self):
        samples = list(self.card.samples("**/Artists/A/kick*"))
        self.assertEqual(len(samples), 1)

    def test_same_sample_in_multiple_settings(self):
        samples = list(self.card.samples("**/DRUMS/Kick/CR78 Kick.wav"))
        for s in samples:
            print(
                s.path,
            )
            for st in s.settings:
                print(st.xml_file.path.name, st.xml_path)
        self.assertEqual(len(samples), 1)
        self.assertEqual(len(samples[0].settings), 3)

    def test_similar_sample_in_multiple_settings(self):
        samples = list(self.card.samples("**/Kick/CR78 Kick.wav"))
        for s in samples:
            print(
                s.path,
            )
            for st in s.settings:
                print(st.xml_file.path.name, st.xml_path)
        self.assertEqual(len(samples), 2)
        self.assertEqual(len(samples[0].settings), 3)
        self.assertEqual(len(samples[1].settings), 0)


class TestMoveSamples(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move')
    @mock.patch('deluge_card.deluge_xml.DelugeXml.write_xml', return_value="filepath")
    def test_move_samples(self, mock_write, mock_move):
        matching = '**/DRUMS/Kick/CR78 Kick.wav'
        new_path = Path('SAMPLES/MV/NEW2.wav')

        movops = list(self.card.mv_samples(matching, new_path))

        for m in movops:
            print(m)

        self.assertEqual(len(movops), 4)
        self.assertEqual(mock_write.call_count, 3)
        self.assertEqual(mock_move.call_count, 1)
