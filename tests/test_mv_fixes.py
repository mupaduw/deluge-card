import inspect
import itertools
import os
from pathlib import Path
from unittest import TestCase, mock, skip

import attr
import attrs

import deluge_card.deluge_song
from deluge_card import DelugeCardFS, DelugeKit, DelugeSong, all_samples, all_used_samples
from deluge_card.deluge_card import InvalidDelugeCard
from deluge_card.deluge_sample import (  # ensure_absolute,; modify_sample_kits,; modify_sample_paths,; modify_sample_songs,; validate_mv_dest,
    Sample,
    mv_samples,
)


class TestBugFix12SongSampleMove(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)
        # p2 = Path(self.cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001.XML')
        # self.song = DelugeSong(self.card, p2)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move')
    @mock.patch('deluge_card.deluge_song.DelugeSong.write_xml', return_value="filepath")
    def test_mv_sample_to_available_relative_dest(self, mock_write, mock_move):

        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)
        matching = '**/Kick/CR78 Kick.wav'
        new_path = Path('SAMPLES/MV')  # valid path

        # print(ssl[:5])
        modops = mv_samples(self.card.card_root, ssl, matching, new_path)
        print()
        print([(m.instance.old_path, m.instance.__hash__()) for m in modops if m.operation == "move_file"])
        self.assertEqual(mock_move.call_count, 1)  # 1 samples in 2 songs
        self.assertEqual(mock_write.call_count, 2)  # 2 songs refer to CR78 Kick


class TestBugFixRabidSongSampleMove(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC02')
        self.card = DelugeCardFS(p)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move')
    @mock.patch('deluge_card.deluge_song.DelugeSong.write_xml', return_value="filepath")
    def test_rabid_dest(self, mock_write, mock_move):
        """
        **/SAMPLES/DRUMS/Rabid-Elephant*Samples/*.* SAMPLES/DRUMS/zaps -s
        """

        # matching = 'SAMPLES/DRUMS/Rabid-Elephant*Samples/*.*'
        matching = '**/RE-Portal*.wav'
        new_path = Path('SAMPLES/MV')  #

        # samples = all_used_samples(self.card, matching)
        # samples = self.card.samples(matching)
        samples = all_samples(self.card, matching)
        ssl = list(samples)

        modops = list(mv_samples(self.card.card_root, ssl, matching, new_path))

        self.assertEqual(mock_move.call_count, 1)  # 1 samples in 1 songs
        self.assertEqual(mock_write.call_count, 5)


class TestBugFixWaldorfSongSynthSampleMove(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC02')
        self.card = DelugeCardFS(p)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move')
    @mock.patch('deluge_card.deluge_xml.DelugeXml.write_xml', return_value="filepath")
    def test_waldorf_dest(self, mock_write, mock_move):
        matching = '**/WaldorfM/Loopop-Waldorf-M-4*/*.*'
        new_path = Path('SAMPLES/MV')  #

        # samples = all_used_samples(self.card, matching)
        # samples = self.card.samples(matching)
        samples = all_samples(self.card, matching)
        ssl = list(samples)

        modops = list(mv_samples(self.card.card_root, ssl, matching, new_path))

        for m in modops:
            print(m)

        song_mods = [m for m in modops if m.operation == "update_song_xml"]
        synth_mods = [m for m in modops if m.operation == "update_synth_xml"]
        sample_mods = [m for m in modops if m.operation == "move_file"]

        self.assertEqual(len(sample_mods), 6)
        self.assertEqual(len(song_mods), 4)
        self.assertEqual(len(synth_mods), 1)  # 4 songs, 1 synth

        self.assertEqual(mock_move.call_count, 6)
        self.assertEqual(mock_write.call_count, 5)  # 4 songs, 1 synth
