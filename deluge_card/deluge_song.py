"""Main classes representing a Deluge Song.

Credit & thanks to Jamie Faye
ref https://github.com/jamiefaye/downrush/blob/master/xmlView/src/SongUtils.js
"""
import typing
from pathlib import Path, PurePath

from lxml import etree

SONGS = 'SONGS'
TOP_FOLDERS = [SONGS, 'SYNTHS', 'KITS', 'SAMPLES']

scale = "C,Db,D,Eb,E,F,Gb,G,Ab,A,Bb,B".split(',')
NOTES = [f'{n}{o}' for o in range(8) for n in scale]
C3_IDX = 36


class SampleSetting:
    """Class representing a sample in the context of a DelugeSong."""

    def __init__(self, song_path, xml_path):
        """Create a new SampleSetting instance.

        Args:
            song_path (Path): Path object for the song.
            xml_path (str): Xmlpath string for the song context.
        """
        self._song_path = song_path
        self._xml_path = xml_path

    def xml_path(self):
        """Path object for the song."""
        return self._xml_path

    def song_path(self):
        """Xmlpath string for the song context."""
        return self._song_path

    def __repr__(self):
        return f"SampleSetting({self._xml_path})"


class Sample:
    """Class representing a Sample file."""

    def __init__(self, filepath: Path):
        """Create a new Sample instance.

        Args:
            filepath (Path): Path object for the sample.
        """
        self._filepath = filepath
        self._song_settings: typing.Dict[str, SampleSetting] = {}

    def add_setting(self, sample_setting):
        """Add a sample setting. sample.

        Args:
            sample_setting (SampleSetting): sample setting.
        """
        self._song_settings[sample_setting.xml_path()] = sample_setting

    def path(self):
        """Path object for the sample."""
        return self._filepath

    def settings(self):
        """Settings for the song."""
        return self._song_settings

    def __repr__(self):
        return f"Sample({self._filepath})"


class DelugeSong:
    """Class representing song data on a DelugeCard (in SONGS/*.xml)."""

    def __init__(self, filepath: Path):
        """Create a new DelugeSong instance.

        Args:
            filepath (Path): Path object for the sample.
        """
        self._filepath = filepath
        self._xmlroot = None

    def path(self):
        """Path object for the song XML file."""
        return self._filepath

    def __repr__(self):
        return f"DelugeSong({self._filepath})"

    def xmlroot(self):
        """Get the xmlroot of the songs XML document."""
        if self._xmlroot is None:
            self._xmlroot = etree.parse(self._filepath).getroot()
            assert self._xmlroot.tag == 'song'
        return self._xmlroot

    def minimum_firmware(self):
        """Get the songs earliest Compatible Firmware version.

        Returns:
            str: earliestCompatibleFirmware version.
        """
        root = self.xmlroot()
        return root.get('earliestCompatibleFirmware')

    def root_note(self):
        """Get the root note.

        Returns:
            str: root note (e.g C).
        """
        root = self.xmlroot()
        note = int(root.get('rootNote')) % 12
        try:
            return NOTES[note + C3_IDX]
        except IndexError as err:
            print(f'note {note} {err}')
            return "64"

    def mode_notes(self):
        """Get the notes in the song scale (mode).

        Returns:
            [int]: list of mode intervals, relative to root.
        """
        root = self.xmlroot()
        notes = root.findall('.//modeNotes/modeNote')
        return [int(e.text) for e in notes]

    def scale_mode(self):
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

    def scale(self):
        """Get the song scale and key.

        Returns:
            str: scale name.
        """
        mode = self.scale_mode()
        root = self.root_note()
        return f'{root[:-1]} {mode}'

    def tempo(self):
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
        root = self.xmlroot()
        fractPart = (int(root.get('timerTickFraction'))) / int('0x100000000', 16)
        # print(int('0x100000000', 16))
        # print(fractPart)
        realTPT = float(root.get('timePerTimerTick')) + fractPart
        # print(realTPT)
        tempo = round((44100 * 60) / (96 * realTPT), 1)
        # tempo = round(55125/realTPT/2, 1)
        return tempo

    def samples(self, pattern: str = ""):
        """Generator for samples referenced in the DelugeSong.

        Args:
            pattern (str): glob-style filename pattern.

        Yields:
            object (Sample): the next sample object.
        """
        root = self.xmlroot()
        tree = etree.ElementTree(root)

        def sample_in_setting(sample_file, tree):
            sample = Sample(Path(sample_file))
            sample.add_setting(SampleSetting(self._filepath, tree.getpath(e)))
            return sample

        for sample_path in [
            './/instruments/kit/soundSources/sound/osc1',
            './/instruments/kit/soundSources/sound/osc2',
            './/osc1/sampleRanges/sampleRange',
        ]:
            for e in root.findall(sample_path):
                sample_file = e.get('fileName')
                if sample_file:
                    if not pattern:
                        yield sample_in_setting(sample_file, tree)
                        continue
                    if PurePath(sample_file).match(pattern):
                        yield sample_in_setting(sample_file, tree)
