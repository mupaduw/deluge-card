import os
from pathlib import Path
from unittest import TestCase, mock

import deluge_card.deluge_song
from deluge_card import DelugeSong


class TestDelugeSong(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001.XML')
        self.song = DelugeSong(p)

    def test_get_minimum_firmware(self):
        self.assertEqual(self.song.minimum_firmware(), '3.1.0-beta')

    def test_get_song_samples(self):
        samples = [s for s in self.song.samples()]
        self.assertEqual(samples[0].path(), Path('SAMPLES/DRUMS/Kick/DDD1 Kick.wav'))
        self.assertEqual(list(samples[0].settings().values())[0].song_path(), self.song.path())
        # print(list(samples[0].settings().values())[0].song_path())
        # assert 0


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
    def test_get_tempe(self):
        self.assertEqual(self.song.tempo(), 96.0)


class TestScales(TestDelugeSong):
    def test_get_root(self):
        self.assertEqual(self.song.root_note(), 'C3')

    def test_get_modenotes(self):
        self.assertEqual(self.song.mode_notes(), [0, 2, 4, 5, 7, 9, 11])  # major scale intervals

    def test_scale_mode(self):
        self.assertEqual(self.song.scale_mode(), 'major')

    def test_scale(self):
        self.assertEqual(self.song.scale(), 'C major')

    # TODO: how to patch lxml
    # @mock.patch('deluge_card.deluge_song.etree._Element')
    @mock.patch('deluge_card.DelugeSong.root_note', return_value='Bb3')
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
        samples = sorted([s.path().name for s in self.card.samples()])
        print(samples)
        self.assertEqual(samples[-1], 'wurgle.wav')
