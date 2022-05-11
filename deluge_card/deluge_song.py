"""Main classes representing a Deluge Song.

Credit & thanks to Jamie Faye
ref https://github.com/jamiefaye/downrush/blob/master/xmlView/src/SongUtils.js
"""
from pathlib import Path, PurePath
from typing import Iterator, List

from attrs import define, field
from lxml import etree

from .deluge_sample import Sample, SampleSetting

SONGS = 'SONGS'
TOP_FOLDERS = [SONGS, 'SYNTHS', 'KITS', 'SAMPLES']

SCALE = "C,Db,D,Eb,E,F,Gb,G,Ab,A,Bb,B".split(',')
NOTES = [f'{n}{o}' for o in range(8) for n in SCALE]
C3_IDX = 36

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    from deluge_card import DelugeCardFS


@define(repr=False, frozen=True)
class DelugeSong:
    """Class representing song data on a DelugeCard (in SONGS/*.xml).

    Attributes:
        path (Path): Path object for the sample file. file.
    """

    cardfs: 'DelugeCardFS'
    path: Path
    xmlroot: etree.ElementTree = field()

    @xmlroot.default
    def _default_xlmroot(self):
        return etree.parse(self.path).getroot()

    def __repr__(self) -> str:
        return f"DelugeSong({self.path})"

    def update_sample_element(self, sample_setting):
        """Update XML element from sample_setting."""
        tree = etree.ElementTree(self.xmlroot)
        elem = tree.find(sample_setting.xml_path.replace('/song/', '//'))
        print('old path', elem.get('fileName'))
        elem.set('fileName', str(sample_setting.sample.path))
        # ss = sample_setting
        # rel_path = ss.sample.path.relative_to(ss.song.cardfs.card_root)
        # elem.set('fileName', str(rel_path))
        return elem

    def write_xml(self, new_path=None) -> str:
        """Write the song XML."""
        filename = new_path or self.path
        with open(filename, 'wb') as doc:
            doc.write(etree.tostring(self.xmlroot, pretty_print=True))
        return str(filename)

    def minimum_firmware(self) -> str:
        """Get the songs earliest Compatible Firmware version.

        Returns:
            str: earliestCompatibleFirmware version.
        """
        return self.xmlroot.get('earliestCompatibleFirmware')

    def root_note(self) -> int:
        """Get the root note.

        Returns:
            int: root note (e.g 36 for C3).
        """
        return int(self.xmlroot.get('rootNote'))

    def mode_notes(self) -> List[int]:
        """Get the notes in the song scale (mode).

        Returns:
            [int]: list of mode intervals, relative to root.
        """
        notes = self.xmlroot.findall('.//modeNotes/modeNote')
        return [int(e.text) for e in notes]

    def scale_mode(self) -> str:
        """Get the descriptive name of the song scale (mode).

        Returns:
            str: scale_mode name.
        """
        mn = self.mode_notes()
        if mn == [0, 2, 4, 5, 7, 9, 11]:
            return 'major'
        if mn == [0, 2, 3, 5, 7, 9, 10]:
            return 'minor'
        if mn == [0, 2, 3, 5, 7, 9, 10]:
            return 'dorian'
        if mn == [0, 1, 3, 5, 7, 8, 10]:
            return 'phrygian'
        if mn == [0, 2, 4, 6, 7, 9, 11]:
            return 'lydian'
        if mn == [0, 2, 4, 5, 7, 9, 10]:
            return 'mixolydian'
        if mn == [0, 1, 3, 5, 6, 8, 10]:
            return 'locrian'
        return 'other'

    def scale(self) -> str:
        """Get the song scale and key.

        Returns:
            str: scale name.
        """
        mode = self.scale_mode()
        root_note = self.root_note() % 12
        return f'{SCALE[root_note]} {mode}'

    def tempo(self) -> float:
        """Get the song tempo in beats per minute.

        Returns:
            float: tempo BPM.

        Javascript:
            [downrush convertTempo()](https://github.com/jamiefaye/downrush/blob
            /a4fa2794002cdcebb093848af501ca17a32abe9a/xmlView/src/SongViewLib.js#L508)
        """
        # // Return song tempo calculated from timePerTimerTick and timerTickFraction
        # function convertTempo(jsong)
        # {
        #     let fractPart = (jsong.timerTickFraction>>>0) / 0x100000000;
        #     let realTPT = Number(jsong.timePerTimerTick) + fractPart;
        #     // Timer tick math: 44100 = standard Fs; 48 = PPQN;
        #     // tempo = (44100 * 60) / 48 * realTPT;
        #     // tempo = 55125 / realTPT
        #     // rounded to 1 place after decimal point:
        #     let tempo = Math.round(551250 / realTPT) / 10;
        #
        #     // console.log("timePerTimerTick=" + jsong.timePerTimerTick + " realTPT= " +  realTPT +
        #     //      " tempo= " + tempo);
        #     // console.log("timerTickFraction=" + jsong.timerTickFraction + " fractPart= " +  fractPart);
        #     return tempo;
        # }
        fractPart = (int(self.xmlroot.get('timerTickFraction'))) / int('0x100000000', 16)
        # print(int('0x100000000', 16))
        # print(fractPart)
        realTPT = float(self.xmlroot.get('timePerTimerTick')) + fractPart
        # print(realTPT)
        tempo = round((44100 * 60) / (96 * realTPT), 1)
        # tempo = round(55125/realTPT/2, 1)
        return tempo

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

        for e in self.xmlroot.findall(".//*[@fileName]"):
            # print(f'elem {e}')
            sample_file = e.get('fileName')
            if sample_file:
                if not pattern:
                    yield sample_in_setting(sample_file, tree)
                    continue
                if PurePath(sample_file).match(pattern):
                    yield sample_in_setting(sample_file, tree)
