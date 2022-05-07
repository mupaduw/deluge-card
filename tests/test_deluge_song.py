import inspect
import os
from pathlib import Path
from unittest import TestCase, mock

import attr
import attrs

import deluge_card.deluge_song
from deluge_card import DelugeSong
from deluge_card.deluge_song import Sample


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


# from functools import map
import itertools


class TestSongSampleMove(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_move_samples(self):

        # get the flat list of all song_samples
        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))

        ssl = list(song_samples)

        print([s.path for s in ssl[:2]])

        # get the list of samples to be moved
        old_path = Path('SAMPLES/Artists/Leonard Ludvigsen/Hangdrum/2.wav')

        def mv_match(sample):
            # try Path parent/child here https://stackoverflow.com/a/34236245
            return str(old_path) == str(sample.path)

        moving_samples = list(filter(mv_match, ssl))
        print(moving_samples)
        print()

        # update paths for the matched
        new_path = Path('SAMPLES/MV/Hangdrum/2.wav')

        def replace_path(sample):
            sample.path = Path(str(sample.path).replace(str(old_path), str(new_path)))
            return sample

        moved_samples = list(map(replace_path, moving_samples))
        print("moved:", moved_samples)
        print()
        updated_samples = list(filter(lambda s: str(new_path) == str(s.path), ssl))
        print("updated:", updated_samples)
        print()
        self.assertEqual(moved_samples, updated_samples)

        updated_songs = set()
        for sample in updated_samples:
            for setting in sample.settings:
                elem = setting.song.update_sample_element(setting)
                assert elem.get('fileName') == str(sample.path)
                updated_songs.add(setting.song)

        print(updated_songs)
        # write the modified XML
        for s in updated_songs:
            s.write_xml(new_path=Path("hacked.XML"))

        assert 0
