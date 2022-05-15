"""Main class representing a Deluge Filesystem in a folder or a mounted SD card."""

from pathlib import Path, PurePath
from typing import Iterator

from attrs import define, field

from .deluge_kit import DelugeKit
from .deluge_sample import Sample, all_samples
from .deluge_song import DelugeSong
from .deluge_synth import DelugeSynth

SONGS = 'SONGS'
SAMPLES = 'SAMPLES'
KITS = 'KITS'
SYNTHS = 'SYNTHS'
TOP_FOLDERS = [SONGS, SYNTHS, KITS, SAMPLES]


def list_deluge_fs(folder) -> Iterator['DelugeCardFS']:
    """List deluge_card look-alike filesystems.

    Args:
        folder (str): path of target folder.

    Yields:
        cards (Iterator[DelugeCardFS]): generator of DelugeCardFS instances.
    """

    def _test_card_fs(folder):
        try:
            return DelugeCardFS.from_folder(folder)
        except InvalidDelugeCard:
            return

    card = _test_card_fs(folder)
    if card:
        yield card
    for fldr in Path(folder).iterdir():
        card = _test_card_fs(fldr)
        if not card:
            continue
        yield card


class InvalidDelugeCard(Exception):
    """This is not a valid DelugeCard FS."""

    def __init__(self, msg):
        """Create a new InvalidDelugeCard Exception.

        Attributes:
            msg (str): Human readable string describing the exception.
        """
        msg: str


@define(frozen=True)
class DelugeCardFS:
    """Main class representing a Deluge SD card/folder structure.

    Attributes:
        card_root (Path): Path object for the root folder.
    """

    card_root: Path = field()

    @card_root.validator
    def _check_card_root(self, attribute, value):
        if not value.is_dir():
            raise InvalidDelugeCard(f'{value} is not a directory path.')
        for folder in TOP_FOLDERS:
            if not Path(value, folder).exists():
                raise InvalidDelugeCard(f'required folder {folder} does not exist in path {value}')

    @staticmethod
    def initialise(path: str) -> 'DelugeCardFS':
        """Create a new Deluge Folder structure.

        Args:
            path (str): a valid folder name.

        Returns:
            instance (DelugeCardFS): new instance.
        """
        card_root = Path(path)
        assert card_root.is_dir()
        # assert card_root.is_mount()
        assert len(list(card_root.iterdir())) == 0

        for folder in TOP_FOLDERS:
            Path(card_root, folder).mkdir()

        return DelugeCardFS(card_root)  # type: ignore

    @staticmethod
    def from_folder(folder: str) -> 'DelugeCardFS':
        """New instance from a Deluge Folder structure.

        Args:
            folder (str): valid folder name.

        Returns:
            instance (DelugeCardFS): new instance.
        """
        return DelugeCardFS(Path(folder))

    def is_mounted(self) -> bool:
        """Is this a mounted SD card.

        Returns:
            mounted (bool): True if card_root is a mounted filesystem.

        Raises:
            err (Exception): on windows is_mount isnpt available
        """
        return Path(self.card_root).is_mount()

    def songs(self, pattern: str = "") -> Iterator['DelugeSong']:
        """Generator for songs in the Card.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (DelugeSong): the next song on the card.
        """
        for songfile in sorted(Path(self.card_root, SONGS).glob('*.XML')):
            if not pattern:
                yield DelugeSong(self, songfile)  # type: ignore
                continue
            if PurePath(songfile).match(pattern):
                yield DelugeSong(self, songfile)

    def kits(self, pattern: str = "") -> Iterator['DelugeKit']:
        """Generator for kits in the Card.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (DelugeKit): the next kit on the card.
        """
        for filepath in sorted(Path(self.card_root, KITS).glob('*.XML')):
            if not pattern:
                yield DelugeKit(self, filepath)  # type: ignore
                continue
            if PurePath(filepath).match(pattern):
                yield DelugeKit(self, filepath)

    def synths(self, pattern: str = "") -> Iterator['DelugeSynth']:
        """Generator for synths in the Card.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (DelugeSynth): the next synth on the card.
        """
        for filepath in sorted(Path(self.card_root, SYNTHS).glob('*.XML')):
            if not pattern:
                yield DelugeSynth(self, filepath)  # type: ignore
                continue
            if PurePath(filepath).match(pattern):
                yield DelugeSynth(self, filepath)

    def samples(self, pattern: str = "") -> Iterator['Sample']:
        """Generator for samples in the Card.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (Sample): the next sample on the card.
        """
        return all_samples(self, pattern)
