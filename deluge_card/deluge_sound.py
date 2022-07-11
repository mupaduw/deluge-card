"""Main class representing a Deluge Sound - used in Synth, Kit and Song XML."""

import enum
from dataclasses import dataclass, field

import lxml.etree

from .deluge_synth import DelugeSynth


class Polyphony(enum.Enum):
    """Enumerate the synth polyphony modes."""

    # name = value
    polyphonic = 'poly'
    auto = 'auto'
    choke = 'choke'


class SynthMode(enum.Enum):
    """Enumerate the synth engine modes."""

    subtractive = 'subtractive'


class LpfMode(enum.Enum):
    """Enumerate the Low-pass filter modes."""

    _12dB = '12dB'
    _24dB = '24dB'


class ModFxType(enum.Enum):
    """Enumerate the Mod FX options."""

    none = 'none'
    phaser = 'phaser'


def attr_or_elem(elem: lxml.etree._Element, name: str, cast=str):
    """Deluge Sytth/Sound are similar forms but the former uses elements and the latter uses attributes."""
    rval = None
    try:
        if elem.get(name):
            rval = elem.get(name)
        else:
            rval = elem.getroottree().find(f'.//{name}').text
    except Exception as err:
        print('got exception', name, rval, cast)
        raise err
    return cast(rval)


class Base(object):
    """https://stackoverflow.com/a/59987363."""

    def __post_init__(self):
        # just intercept the __post_init__ calls so they
        # aren't relayed to `object`
        pass


@dataclass
class NamedSound(Base):
    """A sound base class."""

    name: str = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.name = attr_or_elem(self.sound, 'name')
        # print('NamedSound.__post_init__ named:', self.name)


@dataclass
class PolyphonicSound(Base):
    """A polyphonic composable class."""

    polyphonic: Polyphony = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.polyphonic = Polyphony(attr_or_elem(self.sound, 'polyphonic'))


@dataclass
class PresetSound(Base):
    """A preset composable class."""

    preset_slot: int = field(init=False)
    preset_sub_slot: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.preset_slot = attr_or_elem(self.sound, 'presetSlot')
        self.preset_sub_slot = attr_or_elem(self.sound, 'presetSubSlot')


@dataclass
class BaseSound(Base):
    """A sound base class."""

    sound: lxml.etree._Element
    lpf_mode: LpfMode = field(init=False)
    mode: SynthMode = field(init=False)
    mod_fx_type: str = field(init=False)
    voice_priority: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.mode = SynthMode(attr_or_elem(self.sound, 'mode'))
        self.lpf_mode = LpfMode(attr_or_elem(self.sound, 'lpfMode'))
        self.mod_fx_type = ModFxType(attr_or_elem(self.sound, 'modFXType'))
        self.voice_priority = attr_or_elem(self.sound, 'voicePriority', int)


@dataclass
class DelugeSynthSound(BaseSound, PolyphonicSound):
    """A synth sound."""

    transpose: int = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        self.transpose = int(self.sound.getroottree().find('./transpose').text)

    @staticmethod
    def from_synth(synth: DelugeSynth) -> 'DelugeSynthSound':
        """Get synth from Synth XML (aka Synth Preset)."""
        print(
            f'from_synth {synth.xmlroot} {synth.xmlroot.keys()} {synth.xmlroot.get("polyphonic")} {dir(synth.xmlroot)}'
        )
        return DelugeSynthSound(synth.xmlroot)


@dataclass
class DelugeSongSound(BaseSound, PolyphonicSound, PresetSound):
    """A song instrument synth sound."""

    # activeModFunction: bool = field(init=False)
    default_velocity: int = field(init=False)
    is_armed: bool = field(init=False)

    def __post_init__(self):
        super().__post_init__()
        # self.activeModFunction = attr_or_elem(self.sound, 'activeModFunction', )
        self.default_velocity = attr_or_elem(self.sound, 'defaultVelocity', int)
        self.is_armed = attr_or_elem(self.sound, 'isArmedForRecording', bool)


@dataclass
class DelugeSongKitSound(BaseSound, NamedSound):
    """A song instrument sound."""

    # activeModFunction: bool = field(init=False)
    def __post_init__(self):
        # NamedSound.__post_init__(self)
        super().__post_init__()
