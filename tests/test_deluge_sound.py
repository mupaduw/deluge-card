import itertools
import os
from pathlib import Path
from unittest import TestCase, mock

from lxml import etree

from deluge_card import DelugeCardFS, DelugeSong, DelugeSynth
from deluge_card.deluge_sound import DelugeSongSound, DelugeSynthSound, LpfMode, ModFxType, Polyphony, SynthMode


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

    def test_transpose(self):
        sound = DelugeSynthSound.from_synth(self.synth)
        self.assertEqual(sound.transpose, -12)

    def test_LPF_mode(self):
        sound = DelugeSynthSound.from_synth(self.synth)
        self.assertEqual(sound.lpf_mode.value, '24dB')


class TestSoundFromSynthExtra(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        p2 = Path(self.cwd, 'fixtures', 'DC01', 'SYNTHS', '11-STRINGS1.XML')
        self.card = DelugeCardFS(Path(self.cwd, 'fixtures', 'DC01'))
        self.synth = DelugeSynth(self.card, p2)

    def test_transpose(self):
        sound = DelugeSynthSound.from_synth(self.synth)
        self.assertEqual(sound.transpose, 0)  # default value if no tranpose settings

    def test_synth_numeric_polyphonic_attrib(self):
        """Synth with polyphony = '1'."""
        p = Path(self.cwd, 'fixtures', 'DC01', 'SYNTHS', 'SYNT000.XML')
        synth = DelugeSynth(self.card, p)
        sound = DelugeSynthSound.from_synth(synth)
        self.assertEqual(sound.polyphonic, Polyphony('poly'))


class TestSongBase(TestCase):
    def setUp(self):
        self.cwd = os.path.dirname(os.path.realpath(__file__))
        self.card = DelugeCardFS(Path(self.cwd, 'fixtures', 'DC01'))
        p = Path(self.cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001.XML')
        self.song = DelugeSong(self.card, p)


class TestSynthSoundsFromSong(TestSongBase):
    def test_base_sound_attribs(self):
        sound = list(self.song.synths)[0]
        self.assertEqual(sound.polyphonic.value, 'poly')
        self.assertEqual(sound.mode.value, 'subtractive')
        self.assertEqual(sound.lpf_mode.value, '12dB')
        print(sound, dir(sound))
        self.assertEqual(sound.mod_fx_type, ModFxType.none)
        self.assertEqual(sound.voice_priority, 1)

    def test_song_sound_attribs(self):
        sound = list(self.song.synths)[0]
        self.assertEqual(sound.preset_slot, "133")
        self.assertEqual(sound.preset_sub_slot, "-1")

    def test_song2_sound_attribs(self):
        """Song with missing presetSlot."""
        p2 = Path(self.cwd, 'fixtures', 'DC01', 'SONGS', 'SONG001B.XML')
        song2 = DelugeSong(self.card, p2)

        sound = list(song2.synths)[0]
        self.assertEqual(sound.preset_slot, None)
        self.assertEqual(sound.preset_sub_slot, None)


class TestKitSoundsFromSong(TestSongBase):
    def setUp(self):
        super().setUp()
        self.kit = list(self.song.kits)[0]
        self.sounds = list(self.kit.sounds)

    def test_sound_synth_mode(self):
        self.assertEqual(self.sounds[0].mode.value, 'subtractive')

    def test_lpf_mode(self):
        self.assertEqual(self.sounds[0].lpf_mode, LpfMode._24dB)
        print(self.sounds[0])
        print(self.sounds[0], dir(self.sounds[0]))

    def test_mod_fx_type(self):
        self.assertEqual(self.sounds[0].mod_fx_type, ModFxType.none)

    def test_voice_priority(self):
        self.assertEqual(self.sounds[0].voice_priority, 1)

    # def test_song_sound_attribs(self):
    #     kit = list(self.song.kits)[0]
    #     sound = list(kit.sounds)[0]
    #     self.assertEqual(kit.preset_slot, "133")
    #     self.assertEqual(kit.preset_sub_slot, "-1")
    #     self.assertEqual(kit.name, 'quail')

    # def test_sound_mode(self):
    #     sound = DelugeSynthSound.from_synth(self.synth)
    #     self.assertEqual(sound.mode.name, SynthMode('subtractive').name)
    #     self.assertEqual(sound.mode.name, 'subtractive')
    #     self.assertEqual(sound.mode.value, 'subtractive')

    # def test_trsnpose(self):
    #     sound = DelugeSynthSound.from_synth(self.synth)
    #     print(dir(sound))
    #     self.assertEqual(sound.transpose, -12)
