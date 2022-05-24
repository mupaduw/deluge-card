"""Base class for a Deluge XML file."""

import io
from pathlib import Path, PurePath
from typing import Dict, Iterator

from attrs import define, field
from lxml import etree

from .deluge_sample import Sample, SampleSetting
from .helpers import ensure_absolute

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    from deluge_card import DelugeCardFS


def read_and_clean_xml(xml_path):
    """Strip illegal elements."""
    newxml = io.BytesIO()
    with open(xml_path, 'rb') as f:
        lcount = 0
        for line in f.readlines():
            lcount += 1
            if b'<firmwareVersion>' == line[:17] and lcount < 3:
                continue
            if b'<earliestCompatibleFirmware>' == line[:28] and lcount < 4:
                continue
            newxml.write(line)
    newxml.seek(0)
    return newxml


@define
class DelugeXml:
    """Class representing XML n a DelugeCard (in SONG|KIT|SYNTH xml).

    Attributes:
        cardfs (DelugeCardFS): Card folder system containing this file.
        path (Path): Path object for the sample file. file.
    """

    cardfs: 'DelugeCardFS'
    path: Path
    xmlroot: etree.ElementTree = field(init=False)
    uniqid: int = field(init=False)
    # samples_xpath: str = field(init=False)
    root_elem: str = field(init=False)

    def __attrs_post_init__(self):
        self.uniqid = hash(f'{str(self.cardfs.card_root)}{str(self.path)}')
        # ultimately we might want to lazy load here ....
        # see https://stackoverflow.com/questions/55548536/python-attrs-class-attribute-cached-lazy-load
        try:
            parser = etree.XMLParser(recover=True)
            self.xmlroot = etree.parse(read_and_clean_xml(self.path), parser).getroot()
        except Exception as err:
            print(f'parsing {self.path} raises.')
            raise err

    def __eq__(self, other):
        return self.uniqid == other.uniqid

    def __hash__(self):
        return self.uniqid

    def update_sample_element(self, xml_path, sample_path):
        """Update XML element from sample_setting."""
        tree = etree.ElementTree(self.xmlroot)
        elem = tree.find(xml_path.replace(f'/{self.root_elem}/', '//'))
        # print('DEBUG old path', elem.get('fileName'), elem)
        sample_path = sample_path.relative_to(self.cardfs.card_root)
        if elem.tag == 'fileName':
            elem.text = str(sample_path)
        else:
            elem.set('fileName', str(sample_path))
        return elem

    def write_xml(self, new_path=None) -> str:
        """Write the song XML."""
        filename = new_path or self.path
        with open(filename, 'wb') as doc:
            doc.write(etree.tostring(self.xmlroot, pretty_print=True))
        return str(filename)

    def samples(self, pattern: str = "", allow_missing=False) -> Iterator[Sample]:
        """Generator for samples referenced in the DelugeXML file.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (Sample): the next sample object.
        """
        tree = etree.ElementTree(self.xmlroot)
        sample_map: Dict[Path, Sample] = dict()

        def update_sample_map(sample_file, tree) -> None:
            sample = Sample(ensure_absolute(self.cardfs.card_root, Path(sample_file)))
            if sample.path in sample_map.keys():
                sample = sample_map[sample.path]
            else:
                sample_map[sample.path] = sample
            sample.settings.append(SampleSetting(self, sample, tree.getpath(e)))

        def match_pattern(sample_file: str, pattern: str) -> None:
            if sample_file:
                if (not allow_missing) and (not ensure_absolute(self.cardfs.card_root, Path(sample_file)).exists()):
                    return
                if not pattern:
                    update_sample_map(sample_file, tree)
                elif PurePath(sample_file).match(pattern):
                    update_sample_map(sample_file, tree)

        for e in self.xmlroot.findall(".//*[@fileName]"):
            match_pattern(e.get('fileName'), pattern)

        for e in self.xmlroot.findall(".//fileName"):
            match_pattern(e.text, pattern)

        return (m for m in sample_map.values())
