"""Main class representing a Deluge Sound - used in Synth, Kit and Song XML."""

import enum
from dataclasses import dataclass, field

import lxml.etree

from .deluge_synth import DelugeSynth


class Polyphony(enum.Enum):
    """Enumerate the available synth polyphony modes."""

    # name = value
    polyphonic = 'poly'
    auto = 'auto'
    choke = 'choke'


class SynthMode(enum.Enum):
    """Enumerate the available synth engine modes."""

    subtractive = 'subtractive'


class LpfMode(enum.Enum):
    """Enumerate the available synth engine modes."""

    _12dB = '12dB'
    _24dB = '24dB'


def attr_or_elem(elem: lxml.etree._Element, name: str, cast=str):
    """Deluge Sytth/Sound are similar forms but the former uses elements and the latter uses attributes."""
    if elem.get(name):
        rval = elem.get(name)
    else:
        rval = elem.getroottree().find(f'.//{name}').text
    print(name, rval, cast)
    return cast(rval)


@dataclass
class BaseSound:
    """A sound base class."""

    sound: lxml.etree._Element
    name: str = field(init=False)
    lpf_mode: LpfMode = field(init=False)
    mode: SynthMode = field(init=False)
    mod_fx_type: str = field(init=False)
    polyphonic: Polyphony = field(init=False)
    voice_priority: int = field(init=False)

    def __post_init__(self):
        self.name = self.sound.get('name')
        self.polyphonic = Polyphony(attr_or_elem(self.sound, 'polyphonic'))
        self.mode = SynthMode(attr_or_elem(self.sound, 'mode'))
        self.lpf_mode = LpfMode(attr_or_elem(self.sound, 'lpfMode'))
        self.mod_fx_type = attr_or_elem(self.sound, 'modFXType')
        self.voice_priority = attr_or_elem(self.sound, 'voicePriority', int)


@dataclass
class DelugeSynthSound(BaseSound):
    """A synth sound."""

    transpose: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.transpose = int(self.sound.getroottree().find('./transpose').text)
        print("transpose", self.transpose)

    @staticmethod
    def from_synth(synth: DelugeSynth) -> 'DelugeSynthSound':
        """Get synth from Synth XML (aka Synth Preset)."""
        print(
            f'from_synth {synth.xmlroot} {synth.xmlroot.keys()} {synth.xmlroot.get("polyphonic")} {dir(synth.xmlroot)}'
        )
        return DelugeSynthSound(synth.xmlroot)


@dataclass
class DelugeSongSound(BaseSound):
    """A song instrument sound."""

    # activeModFunction: bool = field(init=False)
    defaultVelocity: int = field(init=False)
    isArmedForRecording: bool = field(init=False)
    presetSlot: int = field(init=False)
    presetSubSlot: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        # self.activeModFunction = attr_or_elem(self.sound, 'activeModFunction', )
        self.defaultVelocity = attr_or_elem(self.sound, 'defaultVelocity', int)
        self.isArmedForRecording = attr_or_elem(self.sound, 'isArmedForRecording', bool)

    # @staticmethod
    # def from_song(song: 'DelugeSong') -> 'DelugeSongSound':
    #     """Get a sy
    #     # print(f'from_synth {synth.xmlroot} {synth.xmlroot.keys()} {synth.xmlroot.get("polyphonic")}
    #       {dir(synth.xmlroot)}')
    #     return DelugeSongSound(synth.xmlroot)


@dataclass
class DelugeSongKitSound(BaseSound):
    """A song instrument sound."""

    # activeModFunction: bool = field(init=False)

    def __post_init__(self):
        super().__post_init__()
