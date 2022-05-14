import itertools
import os
from pathlib import Path
from unittest import TestCase, mock

from lxml import etree

from deluge_card import DelugeCardFS, DelugeSynth
from deluge_card.deluge_sample import ensure_absolute, modify_sample_paths, modify_sample_synths, mv_samples


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

    def test_update_xml(self):

        p2 = Path(self.cwd, 'fixtures', 'DC01', 'SYNTHS', 'SYNT991A.XML')
        synth = DelugeSynth(self.card, p2)

        samples = itertools.chain.from_iterable(map(lambda synth: synth.samples(), self.card.synths()))
        ssl = list(samples)

        for s in ssl:
            print(s)

        matching = '**/DX7/*.wav'
        new_path = Path('SAMPLES/MV3/DX7/NEW2.wav')

        root = self.card.card_root
        new_path = ensure_absolute(root, new_path)

        sample_move_ops = list(modify_sample_paths(root, ssl, matching, new_path))
        updated = list(modify_sample_synths([mo.sample for mo in sample_move_ops]))

        self.assertEqual([synth.path], [us.path for us in updated])


class TestMoveSamples(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move')
    @mock.patch('deluge_card.deluge_xml.DelugeXml.write_xml', return_value="filepath")
    def test_mv_sample_to_available_relative_dest(self, mock_write, mock_move):

        matching = '**/DX7/*.wav'
        new_path = Path('SAMPLES/MV')
        all_sample_gens = itertools.chain(
            map(lambda synth: synth.samples(), self.card.synths()), map(lambda sng: sng.samples(), self.card.songs())
        )
        samples = itertools.chain.from_iterable(all_sample_gens)

        ssl = list(samples)

        moves = list(mv_samples(self.card.card_root, ssl, matching, new_path))
        song_moves = list(filter(lambda m: 'song' in m.operation, moves))
        self.assertEqual(len(song_moves), 0)

        synth_moves = list(filter(lambda m: 'synth' in m.operation, moves))
        self.assertEqual(len(synth_moves), 1)
        # for s in kit_moves:
        #     print(s)
        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(mock_move.call_count, 1)
