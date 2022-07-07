"""Main class representing a Deluge Sound - used in Synth, Kit and Song XML."""

import enum
from dataclasses import dataclass, field

import lxml.etree


class Polyphony(enum.Enum):
    """Enumerate the available synth polyphony modes."""

    poly = 'poly'
    auto = 'auto'
    choke = 'choke'


class SynthMode(enum.Enum):
    """Enumerate the available synth engine modes."""

    subtractive = 'subtractive'


@dataclass
class DelugeSound:
    """A sound aka a Synth."""

    sound: lxml.etree._Element
    name: str = field(init=False)
    polyphonic: Polyphony = field(init=False)
    mode: SynthMode = field(init=False)

    def __post_init__(self):
        self.name = self.sound.get('name')
        self.polyphonic = Polyphony(self.sound.get('polyphonic')).value
        self.mode = SynthMode(self.sound.get('mode')).value
