"""Main class representing a Deluge Filesystem in a folder or a mounted SD card."""

from pathlib import Path

from .deluge_song import DelugeSong, Sample

SONGS = 'SONGS'
SAMPLES = 'SAMPLES'
TOP_FOLDERS = [SONGS, 'SYNTHS', 'KITS', SAMPLES]
SAMPLE_TYPES = {".wav", ".mp3", ".aiff", ".ogg"}


def _test_card_fs(folder):
    try:
        return DelugeCardFS(Path(folder))
    except InvalidDelugeCard:
        return


def list_deluge_fs(folder):
    """List deluge_card look-alike filesystems.

    Args:
        folder (str): path of target folder.

    Returns:
        [DelugeCardFS]: list of DelugeCardFS instances.
    """
    card = _test_card_fs(folder)
    if card:
        return [card]

    res = []
    for fldr in Path(folder).iterdir():
        card = _test_card_fs(fldr)
        if card:
            res.append(card)
    return res


class InvalidDelugeCard(Exception):
    """This is not a valid DelugeCard FS."""

    def __init__(self, msg):
        """Create a new InvalidDelugeCard Exception.

        Args:
            msg (str): Human readable string describing the exception.

        Attributes:
            msg (str): Human readable string describing the exception.
        """
        self.msg = msg


class DelugeCardFS:
    """Main class representing a Deluge SD card/folder structure."""

    @staticmethod
    def initialise(path: str):
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

        return DelugeCardFS(card_root)

    def __init__(self, card_root: Path):
        """Create a new DelugeCardFS instance.

        Args:
            card_root (Path): Path object for the root folder.
        """
        self._card_root = card_root
        self._is_real_card = card_root.is_mount()  # TODO revisit & test this

        card_root.is_dir()
        for folder in TOP_FOLDERS:
            if not Path(card_root, folder).exists():
                raise InvalidDelugeCard(f'required folder {folder} does not exist in path {card_root}')

    def card_root(self):
        """Get card root path.

        Returns:
           card_root (pathlib.Path): path of card_root.
        """
        return self._card_root

    def is_mounted(self):
        """Is this a mounted SD card.

        Returns:
            boolean: True is card_root is a mount.
        """
        return Path(self._card_root).is_mount()

    def songs(self):
        """Generator for songs in the Card.

        Yields:
            DelugeSong: the next song on the card.
        """
        for songfile in sorted(Path(self._card_root, SONGS).glob('*.XML')):
            yield DelugeSong(songfile)

    def samples(self):
        """Generator for samples in the Card.

        Yields:
            Sample: the next sample on the card.
        """
        smp = Path(self._card_root, SAMPLES)
        paths = (p.resolve() for p in Path(smp).glob("**/*") if p.suffix.lower() in SAMPLE_TYPES)
        for fname in paths:
            yield Sample(Path(fname))
