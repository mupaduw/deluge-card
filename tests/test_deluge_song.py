import inspect
import itertools
import os
from pathlib import Path
from unittest import TestCase, mock

import attr
import attrs

import deluge_card.deluge_song
from deluge_card import DelugeSong
from deluge_card.deluge_sample import Sample, mv_samples


class TestSampleAttr(TestCase):
    def test_initialise(self):
        print(inspect.signature(Sample.__init__))
        mySample = Sample(Path("a/b/c"))
        print(mySample)
        # assert 0


class TestDelugeSong(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001.XML')
        self.song = DelugeSong(p)

    def test_get_minimum_firmware(self):
        self.assertEqual(self.song.minimum_firmware(), '3.1.0-beta')

    def test_get_song_samples(self):
        samples = list(self.song.samples())
        self.assertEqual(samples[0].path, Path('SAMPLES/Artists/Leonard Ludvigsen/Hangdrum/1.wav'))
        print(samples[0])
        self.assertEqual(samples[0].settings[0].song, self.song)
        self.assertEqual(len(samples), 32)


class TestSongSamples(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001.XML')
        self.song = DelugeSong(p)

    def test_list_all_samples(self):
        samples = list(self.song.samples())
        print(samples)
        self.assertEqual(len(samples), 32)

    def test_list_samples_0(self):
        samples = list(self.song.samples("*Snare*"))
        print(samples)
        self.assertEqual(len(samples), 2)

    def test_list_samples_1(self):
        samples = list(self.song.samples("*808*"))
        print(samples)
        self.assertEqual(len(samples), 16)

    def test_list_samples_2(self):
        samples = list(self.song.samples("**/Clap/*"))
        print(samples)
        self.assertEqual(len(samples), 2)


class TestTempo(TestDelugeSong):
    def test_get_tempo(self):
        self.assertEqual(self.song.tempo(), 96.0)


class TestScales(TestDelugeSong):
    def test_get_root(self):
        self.assertEqual(self.song.root_note(), 0)

    def test_get_modenotes(self):
        self.assertEqual(self.song.mode_notes(), [0, 2, 4, 5, 7, 9, 11])  # major scale intervals

    def test_scale_mode(self):
        self.assertEqual(self.song.scale_mode(), 'major')

    def test_scale(self):
        self.assertEqual(self.song.scale(), 'C major')

    # TODO: how to patch lxml
    # @mock.patch('deluge_card.deluge_song.etree._Element')
    @mock.patch('deluge_card.DelugeSong.root_note', return_value=10)
    def test_scale_Bb_major(self, mocked):
        # mocked.parse.return_value =
        # mocked.return_value.get.return_value = -2 #mock.MagicMock(spec='deluge_card.deluge_song.etree.Element', )
        # mocked.get = mock.Mock(return_value = -2)
        key = self.song.scale()
        self.assertEqual(mocked.called, True)
        self.assertEqual(key, 'Bb major')
        self.assertEqual(mocked.call_count, 1)
        # mocked.assert_called_once_with('rootNote')


from deluge_card import DelugeCardFS
from deluge_card.deluge_card import InvalidDelugeCard


class TestDelugeSample(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_list_samples(self):
        samples = sorted([s.path.name for s in self.card.samples()])
        print(samples)
        self.assertEqual(samples[-1], 'wurgle.wav')


from deluge_card.deluge_sample import modify_sample_paths


class TestSongSampleMove(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_move_samples(self):

        # get the flat list of all song_samples
        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)
        matching = '**/Leonard Ludvigsen/Hangdrum/2.wav'
        new_path = Path('SAMPLES/MV2/JOBB/Hangdrum/NEW2.wav')

        moved_samples = [mov.sample for mov in modify_sample_paths(ssl, matching, new_path)]

        print("moved:", moved_samples)
        print()

        def is_relative_to(sample):
            try:
                p = sample.path.relative_to(new_path)
                return True
            except ValueError:
                return False

        updated_samples = list(filter(is_relative_to, ssl))

        # print("updated:", updated_samples)
        # print()
        self.assertEqual(moved_samples, updated_samples)

        # assert 0

    def test_path_glob_replace_mv(self):

        old_path = Path('SAMPLES/Artists/Leonard Ludvigsen/Hangdrum/2.wav')
        new_path = Path('SAMPLES/MV/Hangdrum/')

        self.assertEqual('2.wav', old_path.name)
        self.assertEqual(old_path.parent, Path('SAMPLES/Artists/Leonard Ludvigsen/Hangdrum'))

        new_file = Path(new_path, old_path.name)
        self.assertEqual(new_file, Path('SAMPLES/MV/Hangdrum/2.wav'))
