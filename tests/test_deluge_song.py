import inspect
import itertools
import os
from pathlib import Path
from unittest import TestCase, mock

import attr
import attrs

import deluge_card.deluge_song
from deluge_card import DelugeCardFS, DelugeSong
from deluge_card.deluge_sample import Sample, mv_samples
from deluge_card.helpers import ensure_absolute


class TestSampleAttr(TestCase):
    def test_initialise(self):
        print(inspect.signature(Sample.__init__))
        mySample = Sample(Path("a/b/c"))
        print(mySample)
        # assert 0


class TestDelugeSong(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)
        p = Path(cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001.XML')
        self.song = DelugeSong(self.card, p)

    def test_get_minimum_firmware(self):
        self.assertEqual(self.song.minimum_firmware(), '3.1.0-beta')

    def test_get_song_samples(self):
        samples = list(self.song.samples(allow_missing=True))
        self.assertEqual(
            samples[0].path,
            ensure_absolute(self.card.card_root, Path('SAMPLES/Artists/Leonard Ludvigsen/Hangdrum/1.wav')),
        )
        print(samples[0])
        self.assertEqual(samples[0].settings[0].xml_file, self.song)
        self.assertEqual(len(samples), 32)


class TestSongSamples(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        card = DelugeCardFS(p)
        p = Path(cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001.XML')
        self.song = DelugeSong(card, p)

    def test_list_all_samples(self):
        samples = list(self.song.samples(allow_missing=True))
        print(samples)
        self.assertEqual(len(samples), 32)

    def test_list_samples_0(self):
        samples = list(self.song.samples("*Snare*", allow_missing=True))
        print(samples)
        self.assertEqual(len(samples), 2)

    def test_list_samples_1(self):
        samples = list(self.song.samples("*808*", allow_missing=True))
        print(samples)
        self.assertEqual(len(samples), 16)

    def test_list_samples_2(self):
        samples = list(self.song.samples("**/Clap/*", allow_missing=True))
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


class TestInstrument(TestDelugeSong):
    def test_synth_count(self):
        self.assertEqual(len(list(self.song.synths())), 3)

    def test_kit_count(self):
        self.assertEqual(len(list(self.song.kits())), 2)

    def test_kit_one_sounds(self):
        k1 = list(self.song.kits())[0]
        kit_sounds = list(k1.sounds)
        self.assertEqual(len(kit_sounds), 14)
        self.assertEqual(kit_sounds[0].name, 'KICK')
        self.assertEqual(kit_sounds[13].name, 'TOMH')
