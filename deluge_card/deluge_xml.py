"""Base class for a Deluge XML file."""

import io
from pathlib import Path, PurePath
from typing import Iterator

from attrs import define, field
from lxml import etree

from .deluge_sample import Sample, SampleSetting

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    from deluge_card import DelugeCardFS


def clean_xml(xml_path):
    """Fix bad xml on read."""
    newxml = io.BytesIO()
    with open(xml_path, 'rb') as f:
        for line in f.readlines():
            if b'<firmwareVersion' == line[:16]:
                continue
            newxml.write(line)
    newxml.seek(0)
    return newxml


@define
class DelugeXml:
    """Class representing XML n a DelugeCard (in SONGS/*.xml).

    Attributes:
        cardfs (DelugeCardFS): Card folder system containing this file.
        path (Path): Path object for the sample file. file.
    """

    cardfs: 'DelugeCardFS'
    path: Path
    xmlroot: etree.ElementTree = field(init=False)
    uniqid: int = field(init=False)
    samples_xpath: str = field(init=False)
    root_elem: str = field(init=False)

    def __attrs_post_init__(self):
        self.uniqid = hash(f'{str(self.cardfs.card_root)}{str(self.path)}')
        self.xmlroot = etree.parse(clean_xml(self.path)).getroot()

    def __eq__(self, other):
        return self.uniqid == other.uniqid

    def __hash__(self):
        return self.uniqid

    def update_sample_element(self, sample_setting):
        """Update XML element from sample_setting."""
        tree = etree.ElementTree(self.xmlroot)
        elem = tree.find(sample_setting.xml_path.replace(f'/{self.root_elem}/', '//'))
        # print('DEBUG old path', elem.get('fileName'))
        elem.set('fileName', str(sample_setting.sample.path))
        return elem

    def write_xml(self, new_path=None) -> str:
        """Write the song XML."""
        filename = new_path or self.path
        with open(filename, 'wb') as doc:
            doc.write(etree.tostring(self.xmlroot, pretty_print=True))
        return str(filename)

    def samples(self, pattern: str = "") -> Iterator[Sample]:
        """Generator for samples referenced in the DelugeSong.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (Sample): the next sample object.
        """
        tree = etree.ElementTree(self.xmlroot)

        def sample_in_setting(sample_file, tree) -> Sample:
            sample = Sample(Path(sample_file))
            sample.settings.append(SampleSetting(self, sample, tree.getpath(e)))
            return sample

        for e in self.xmlroot.findall(self.samples_xpath):
            # print(f'elem {e}')
            sample_file = e.get('fileName')
            if sample_file:
                if not pattern:
                    yield sample_in_setting(sample_file, tree)
                    continue
                if PurePath(sample_file).match(pattern):
                    yield sample_in_setting(sample_file, tree)
