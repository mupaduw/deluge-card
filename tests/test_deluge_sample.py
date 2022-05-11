import inspect
import itertools
import os
from pathlib import Path
from unittest import TestCase, mock, skip

import attr
import attrs

import deluge_card.deluge_song
from deluge_card import DelugeCardFS, DelugeSong
from deluge_card.deluge_card import InvalidDelugeCard
from deluge_card.deluge_sample import (
    Sample,
    ensure_absolute,
    modify_sample_paths,
    modify_sample_songs,
    mv_samples,
    validate_mv_dest,
)


class TestDelugeSample(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_list_samples(self):
        samples = sorted([s.path.name for s in self.card.samples()])
        print(samples)
        self.assertEqual(samples[-1], 'wurgle.wav')


class TestValidateDestination(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)

    def test_validate_mv_dest_not_subfolder(self):
        new_path = Path('.').absolute()  # make tthe cwd, and valid
        root = self.card.card_root
        with self.assertRaises(ValueError) as ctx:
            validate_mv_dest(root, new_path)
        self.assertEqual(str(ctx.exception), 'Destination must be a sub-folder of card.')

    def test_validate_mv_dest_invalid2(self):
        new_path = Path('SONGS/MV/NEW2.wav')
        root = self.card.card_root
        with self.assertRaisesRegex(ValueError, 'target folder does not exist:.*SONGS.MV') as ctx:
            validate_mv_dest(root, new_path)

    def test_validate_mv_dest_bad_target(self):
        new_path = Path('SAMPLES/MV2/NEW2.wav')
        root = self.card.card_root
        with self.assertRaisesRegex(ValueError, 'target folder does not exist:.*SAMPLES.MV2') as ctx:
            validate_mv_dest(root, new_path)

    def test_validate_mv_dest_valid(self):
        root = self.card.card_root
        new_path = Path(root, 'SAMPLES/MV/NEW2.wav').absolute()  # make this relative to cwd
        validate_mv_dest(root, new_path)


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


class TestSongSampleMove(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p = Path(self.cwd, 'fixtures', 'DC01')
        self.card = DelugeCardFS(p)
        p2 = Path(self.cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001.XML')
        self.song = DelugeSong(self.card, p2)

    def test_modify_sample_paths(self):
        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)[:2]
        matching = '**/Leonard Ludvigsen/Hangdrum/2.wav'
        new_path = Path('SAMPLES/MV/NEW2.wav')

        root = self.card.card_root
        new_path = ensure_absolute(root, new_path)
        validate_mv_dest(root, new_path)  # raises exception if args are invalid

        moved_samples = [mo.sample for mo in modify_sample_paths(root, ssl, matching, new_path)]

        self.assertEqual(len(moved_samples), 1)
        self.assertEqual(Path(root, moved_samples[0].path), new_path)

    def test_move_samples(self):

        # get the flat list of all song_samples
        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)

        matching = '**/Leonard Ludvigsen/Hangdrum/2.wav'
        new_path = Path('SAMPLES/NEW2.wav')

        root = self.card.card_root
        new_path = ensure_absolute(root, new_path)
        validate_mv_dest(root, new_path)  # raises exception if args are invalid

        moved_samples = [mov.sample for mov in modify_sample_paths(root, ssl, matching, new_path)]

        print("moved:", moved_samples)
        print()

        def is_relative_to(sample):
            # print('is_relative_to', sample.path)
            try:
                p = Path(root, sample.path).relative_to(new_path)
                return True
            except ValueError:
                return False

        updated_samples = list(filter(is_relative_to, ssl))
        self.assertEqual(moved_samples, updated_samples)

    def test_update_song_xml(self):

        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)
        matching = '**/Leonard Ludvigsen/Hangdrum/2.wav'
        new_path = Path('SAMPLES/MV3/JOBB/Hangdrum/NEW2.wav')

        root = self.card.card_root
        new_path = ensure_absolute(root, new_path)

        print("new path", new_path)
        # validate_mv_dest(root, new_path)  # raises exception if args are invalid

        sample_move_ops = list(modify_sample_paths(root, ssl, matching, new_path))

        # print('smo',)
        # for s in sample_move_ops:
        #     print(f"{s.old_path} => {s.new_path}")

        updated_songs = list(modify_sample_songs([mo.sample for mo in sample_move_ops]))
        print(updated_songs)
        self.assertEqual([self.song.path], [us.path for us in updated_songs])

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move')
    @mock.patch('deluge_card.deluge_song.DelugeSong.write_xml', return_value="filepath")
    def test_mv_sample_to_available_relative_dest(self, mock_write, mock_move):

        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)
        matching = '**/Leonard Ludvigsen/Hangdrum/*.wav'
        new_path = Path('SAMPLES/MV')

        print(ssl[:5])
        moves = list(mv_samples(self.card.card_root, ssl, matching, new_path))

        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(mock_move.call_count, 2)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move', return_value=True)
    @mock.patch('deluge_card.deluge_song.DelugeSong.write_xml', return_value="filepath")
    def test_mv_sample_to_available_absolute_dest(self, mock_write, mock_move):

        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)
        matching = '**/Leonard Ludvigsen/Hangdrum/*.wav'
        new_path = Path(self.card.card_root, 'SAMPLES/MV')

        print(ssl[:5])
        moves = list(mv_samples(self.card.card_root, ssl, matching, new_path))

        self.assertEqual(mock_write.call_count, 1)
        self.assertEqual(mock_move.call_count, 2)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move', return_value=True)
    @mock.patch('deluge_card.deluge_song.DelugeSong.write_xml', return_value="filepath")
    def test_mv_sample_to_missing_rel_dest(self, mock_write, mock_move):

        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)
        matching = '**/Leonard Ludvigsen/Hangdrum/*.wav'
        new_path = Path('SAMPLES/MV4/JOBB/')

        # print(ssl[:5])
        with self.assertRaises(ValueError) as err:
            moves = list(mv_samples(self.card.card_root, ssl, matching, new_path))
        # print(err)
        self.assertEqual(mock_write.call_count, 0)
        self.assertEqual(mock_move.call_count, 0)

    @mock.patch('deluge_card.deluge_sample.SampleMoveOperation.do_move', return_value=True)
    @mock.patch('deluge_card.deluge_song.DelugeSong.write_xml', return_value="filepath")
    def test_mv_sample_to_available_invalid_dest(self, mock_write, mock_move):

        song_samples = itertools.chain.from_iterable(map(lambda sng: sng.samples(), self.card.songs()))
        ssl = list(song_samples)
        matching = '**/Leonard Ludvigsen/Hangdrum/*.wav'
        new_path = Path('/tmp')

        # print(ssl[:5])
        with self.assertRaises(ValueError) as err:
            moves = list(mv_samples(self.card.card_root, ssl, matching, new_path))
        # print(err)
        self.assertEqual(mock_write.call_count, 0)
        self.assertEqual(mock_move.call_count, 0)

    def test_path_glob_replace_mv(self):

        old_path = Path('SAMPLES/Artists/Leonard Ludvigsen/Hangdrum/2.wav')
        new_path = Path('SAMPLES/MV/Hangdrum/')

        self.assertEqual('2.wav', old_path.name)
        self.assertEqual(old_path.parent, Path('SAMPLES/Artists/Leonard Ludvigsen/Hangdrum'))

        new_file = Path(new_path, old_path.name)
        self.assertEqual(new_file, Path('SAMPLES/MV/Hangdrum/2.wav'))
