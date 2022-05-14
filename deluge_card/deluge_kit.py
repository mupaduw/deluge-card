"""Main class representing a Deluge Kit."""

from pathlib import Path

from attrs import define

from .deluge_xml import DelugeXml

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    from deluge_card import DelugeCardFS


@define(repr=False)
class DelugeKit(DelugeXml):
    """Class representing kit data on a DelugeCard (in KITS/*.xml).

    Attributes:
        cardfs (DelugeCardFS): Card folder system containing this file.
        path (Path): Path object for the sample file. file.
    """

    cardfs: 'DelugeCardFS'
    path: Path

    def __attrs_post_init__(self):
        self.samples_xpath = ".//fileName"
        self.root_elem = 'kit'
        super(DelugeKit, self).__attrs_post_init__()

    def __repr__(self) -> str:
        return f"DelugeKit({self.path})"
