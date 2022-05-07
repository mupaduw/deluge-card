"""Main class representing a Deluge Filesystem in a folder or a mounted SD card."""

from pathlib import Path, PurePath
from typing import Iterator

from attrs import define, field

from .deluge_song import DelugeSong, Sample

SONGS = 'SONGS'
SAMPLES = 'SAMPLES'
TOP_FOLDERS = [SONGS, 'SYNTHS', 'KITS', SAMPLES]
SAMPLE_TYPES = {".wav", ".mp3", ".aiff", ".ogg"}


def list_deluge_fs(folder) -> Iterator['DelugeCardFS']:
    """List deluge_card look-alike filesystems.

    Args:
        folder (str): path of target folder.

    Returns:
        [DelugeCardFS]: list of DelugeCardFS instances.
    """

    def _test_card_fs(folder):
        try:
            return DelugeCardFS(Path(folder))
        except InvalidDelugeCard:
            return

    card = _test_card_fs(folder)
    if card:
        yield card
    for fldr in Path(folder).iterdir():
        card = _test_card_fs(fldr)
        if not card:
            print(f"not a Deluge FS {folder}")
            continue
        yield card


@define
class InvalidDelugeCard(Exception):
    """This is not a valid DelugeCard FS."""

    def __init__(self, msg):
        """Create a new InvalidDelugeCard Exception.

        Attributes:
            msg (str): Human readable string describing the exception.
        """
        msg: str


@define
class DelugeCardFS:
    """Main class representing a Deluge SD card/folder structure.

    Attributes:
        card_root (Path): Path object for the root folder.
    """

    card_root: str = field()

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

    def is_mounted(self) -> bool:
        """Is this a mounted SD card.

        Returns:
            mounted (bool): True if card_root is a mounted filesystem.

        Raises:
            err (Exception): on windows is_mount isnpt available
        """
        return Path(self.card_root).is_mount()

    def songs(self, pattern: str = "") -> Iterator[DelugeSong]:
        """Generator for songs in the Card.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (DelugeSong): the next song on the card.
        """
        for songfile in sorted(Path(self.card_root, SONGS).glob('*.XML')):
            if not pattern:
                yield DelugeSong(songfile)  # type: ignore
                continue
            if PurePath(songfile).match(pattern):
                yield DelugeSong(songfile)

    def samples(self, pattern: str = "") -> Iterator[Sample]:
        """Generator for samples in the Card.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (Sample): the next sample on the card.
        """
        smp = Path(self.card_root, SAMPLES)
        paths = (p.resolve() for p in Path(smp).glob("**/*") if p.suffix.lower() in SAMPLE_TYPES)
        for fname in paths:
            if not pattern:
                yield Sample(Path(fname))
                continue
            if PurePath(fname).match(pattern):
                yield Sample(Path(fname))
