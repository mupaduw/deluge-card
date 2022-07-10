import itertools
import os
from pathlib import Path
from unittest import TestCase, mock

from lxml import etree

from deluge_card import DelugeCardFS, DelugeSynth
from deluge_card.deluge_sound import DelugeSongSound, DelugeSynthSound, Polyphony, SynthMode


class TestSoundFromSynth(TestCase):
    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        p2 = Path(cwd, 'fixtures', 'DC01', 'SYNTHS', 'SYNT991A.XML')
        self.card = DelugeCardFS(Path(cwd, 'fixtures', 'DC01'))
        self.synth = DelugeSynth(self.card, p2)

    def test_sound_polyphony(self):
        print(f'test_sound_from_synth {self.synth.xmlroot} {self.synth.xmlroot.keys()} {self.synth.xmlroot.sourceline}')
        print([x for x in self.synth.xmlroot])
        sound = DelugeSynthSound.from_synth(self.synth)
        self.assertEqual(sound.polyphonic.name, Polyphony('poly').name)  # polyphonic
        self.assertEqual(sound.polyphonic.name, 'polyphonic')
        self.assertEqual(sound.polyphonic.value, 'poly')

    def test_sound_mode(self):
        sound = DelugeSynthSound.from_synth(self.synth)
        self.assertEqual(sound.mode.name, SynthMode('subtractive').name)
        self.assertEqual(sound.mode.name, 'subtractive')
        self.assertEqual(sound.mode.value, 'subtractive')

    def test_trsnpose(self):
        sound = DelugeSynthSound.from_synth(self.synth)
        print(dir(sound))
        self.assertEqual(sound.transpose, -12)
