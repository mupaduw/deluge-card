import itertools
import os
from pathlib import Path
from unittest import TestCase, mock, skip

from deluge_card.deluge_card import DelugeCardFS, DelugeKit
from deluge_card.deluge_sample import ensure_absolute, modify_sample_kits, modify_sample_paths, mv_samples


class TestKitSamples(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_find_all_kit_samples(self):
        kit_samples = itertools.chain.from_iterable(map(lambda kit: kit.samples(None, True), self.card.kits()))
        ksl = list(kit_samples)
        for s in ksl:
            print(s.path)
        self.assertEqual(len(ksl), 14)  # 14 samples in 1 kit

    def test_find_kit_hihat_samples(self):
        pattern = '**/Hat?/*.wav'
        kit_samples = itertools.chain.from_iterable(
            map(lambda kit: kit.samples(pattern, allow_missing=True), self.card.kits())
        )
        ksl = list(kit_samples)
        self.assertEqual(len(ksl), 2)  # 2 hihat samples in 1 kit

    def test_update_xml(self):

        p2 = Path(self.cwd, 'fixtures', 'DC01', 'KITS', 'KIT014.XML')
        kit = DelugeKit(self.card, p2)

        kit_samples = itertools.chain.from_iterable(map(lambda kit: kit.samples(), self.card.kits()))
        ssl = list(kit_samples)
        matching = '**/Kick/CR78 Kick.wav'
        new_path = Path('SAMPLES/MV3/JOBB/Hangdrum/NEW2.wav')

        root = self.card.card_root
        new_path = ensure_absolute(root, new_path)

        sample_move_ops = list(modify_sample_paths(root, ssl, matching, new_path))
        updated_kits = list(modify_sample_kits(sample_move_ops))

        self.assertEqual([kit.path], [us.path for us in updated_kits])


class TestMoveSamples(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move')
    @mock.patch('deluge_card.deluge_xml.DelugeXml.write_xml', return_value="filepath")
    def test_mv_sample_to_available_relative_dest(self, mock_write, mock_move):

        matching = '**/Kick/CR78 Kick.wav'
        new_path = Path('SAMPLES/MV')
        all_sample_gens = itertools.chain(
            map(lambda kit: kit.samples(), self.card.kits()), map(lambda sng: sng.samples(), self.card.songs())
        )
        samples = itertools.chain.from_iterable(all_sample_gens)

        ssl = list(samples)

        moves = list(mv_samples(self.card.card_root, ssl, matching, new_path))
        song_moves = list(filter(lambda m: 'song' in m.operation, moves))
        self.assertEqual(len(song_moves), 2)

        kit_moves = list(filter(lambda m: 'kit' in m.operation, moves))
        self.assertEqual(len(kit_moves), 1)
        # for s in kit_moves:
        #     print(s)
        self.assertEqual(mock_write.call_count, 3)
        self.assertEqual(mock_move.call_count, 1)
