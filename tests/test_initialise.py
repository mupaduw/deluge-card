import platform
import tempfile
from pathlib import Path
from unittest import TestCase, mock

import deluge_card.deluge_card
from deluge_card import DelugeCardFS
from deluge_card.deluge_card import TOP_FOLDERS, InvalidDelugeCard, list_deluge_fs


class TestInitialiseNew(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_new_card(self):
        card = DelugeCardFS.initialise(self.temp_dir.name)
        self.assertTrue(isinstance(card, DelugeCardFS))
        self.assertTrue(Path(self.temp_dir.name, 'SONGS').is_dir())
        self.assertEqual(len(list(card.songs())), 0)

    def test_open_initialised_card(self):
        # Initialise new CARD
        card = DelugeCardFS.initialise(self.temp_dir.name)

        # now we can open it again
        mycard = DelugeCardFS(Path(self.temp_dir.name))
        self.assertEqual(len(list(mycard.songs())), 0)

    def test_cannot_open_non_card(self):
        with self.assertRaises(InvalidDelugeCard) as ctx:
            mycard = DelugeCardFS(Path(self.temp_dir.name))

    def test_open_legacy_card(self):
        for folder in TOP_FOLDERS:
            Path(self.temp_dir.name, folder).mkdir()

        mycard = DelugeCardFS(Path(self.temp_dir.name))
        self.assertEqual(len(list(mycard.songs())), 0)

    @mock.patch('deluge_card.deluge_card.Path.is_mount', return_value=True)
    def test_is_physical_card(self, mock):
        """this mock will work, regardless of OS.

        But beware, this will raise an exception in Windows.
        """
        if platform.system() == "Windows":
            return
        DelugeCardFS.initialise(self.temp_dir.name)
        mycard = DelugeCardFS(Path(self.temp_dir.name))
        self.assertTrue(mycard.is_mounted())
        self.assertTrue(mock.called)


class TestListDelugeCardFS(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_list_sub_folders(self):

        behaviour = """
		Given that we create a temp folder:
		When we create 2 deluge folders
		and we create one nondeluge folders
		Then we should get a results containing 2 * DelugeCardFS objects
		and a list containing one Path object
		"""
        for fname in ['A', 'B', 'Z']:
            folder = Path(self.temp_dir.name, fname)
            folder.mkdir()
            card = DelugeCardFS.initialise(folder)

        non_deluge = Path(self.temp_dir.name, 'C').mkdir()

        cards = list_deluge_fs(self.temp_dir.name)
        self.assertEqual(len(cards), 3)
        self.assertTrue(isinstance(cards[0], DelugeCardFS))
