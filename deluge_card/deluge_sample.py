"""Main classes representing Deluge Sample."""

import itertools
from pathlib import Path
from typing import Iterator, List

from attrs import define, field

from .helpers import ensure_absolute

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    import deluge_kit
    import deluge_song
    import deluge_synth
    import deluge_xml


def modify_sample_paths(
    root: Path, samples: Iterator['Sample'], pattern: str, dest: Path
) -> Iterator['SampleMoveOperation']:
    """Modify sample paths just as posix mv does."""

    def glob_match(sample) -> bool:
        return Path(sample.path).match(pattern)

    def build_move_op(sample) -> SampleMoveOperation:
        # print('DEBUG:', sample.path)
        if dest.suffix == '':
            move_op = SampleMoveOperation(ensure_absolute(root, sample.path), Path(dest, sample.path.name), sample)
        else:
            move_op = SampleMoveOperation(ensure_absolute(root, sample.path), Path(dest), sample)
        # sample.path = move_op.new_path.relative_to(root)
        return move_op

    matching_samples = filter(glob_match, samples)
    return map(build_move_op, matching_samples)


@define
class SettingElementUpdater(object):
    """Setting updater class.

    Attributes:
        root_xml_path (str): type or root node : /song/, /kit/, or /sound/.
    """

    root_xml_path: str

    def update_settings(self, move_op: 'SampleMoveOperation'):
        """Update settings."""
        # print(f"DEBUG update_song_elements: {sample}")
        for setting in move_op.sample.settings:
            if not setting.xml_path[: len(self.root_xml_path)] == self.root_xml_path:
                continue
            # print(f"DEBUG update_song_elements setting: {setting}")
            setting.xml_file.update_sample_element(setting.xml_path, move_op.new_path)
            yield setting.xml_file


def modify_sample_songs(move_ops: List['SampleMoveOperation']) -> Iterator['deluge_song.DelugeSong']:
    """Update song XML elements."""
    updater = SettingElementUpdater('/song/')
    return itertools.chain.from_iterable(map(updater.update_settings, move_ops))


def modify_sample_kits(move_ops: List['SampleMoveOperation']) -> Iterator['deluge_kit.DelugeKit']:
    """Update kit XML elements."""
    updater = SettingElementUpdater('/kit/')
    return itertools.chain.from_iterable(map(updater.update_settings, move_ops))


def modify_sample_synths(move_ops: List['SampleMoveOperation']) -> Iterator['deluge_synth.DelugeSynth']:
    """Update synth XML elements."""
    updater = SettingElementUpdater('/sound/')
    return itertools.chain.from_iterable(map(updater.update_settings, move_ops))


def validate_mv_dest(root: Path, dest: Path):
    """Check: dest path must be a child of root and must exist."""
    absolute_dest = ensure_absolute(root, dest)

    # file as target
    if absolute_dest.suffix:  # looks like a file target
        if not absolute_dest.parent.exists():
            raise ValueError(f"target folder does not exist: {dest}")
    # folder as target
    elif not (absolute_dest.is_dir()):
        raise ValueError(f"target folder does not exist: {dest}")

    try:
        absolute_dest.parent.relative_to(root)
    except ValueError:
        raise ValueError("Destination must be a sub-folder of card.")


def mv_samples(root: Path, samples: Iterator['Sample'], pattern: str, dest: Path):
    """Move samples, updating any affected XML files."""
    dest = ensure_absolute(root, dest)
    validate_mv_dest(root, dest)  # raises exception if args are invalid

    sample_move_ops = list(modify_sample_paths(root, samples, pattern, dest))  # materialise the list

    updated_songs = set(modify_sample_songs(sample_move_ops))
    updated_kits = set(modify_sample_kits(sample_move_ops))
    updated_synths = set(modify_sample_synths(sample_move_ops))

    # write the modified XML, per unique song, kit, synth
    # TODO this is writing files multiple times
    for updated, tag in [(updated_songs, 'song'), (updated_kits, 'kit'), (updated_synths, 'synth')]:
        for xml in updated:
            xml.write_xml()
            yield ModOp(f"update_{tag}_xml", str(xml.path), xml)

    # move the samples
    for move_op in set(sample_move_ops):
        move_op.do_move()
        yield ModOp("move_file", str(move_op.new_path), move_op)


@define(eq=False)
class SampleMoveOperation(object):
    """Represents a sample file move operation.

    Attributes:
        old_path (Path): original Path.
        new_path (Path): new Path.
        sample (Sample): sample instance.
    """

    old_path: Path
    new_path: Path
    sample: 'Sample'
    uniqid: int = field(init=False)

    def __attrs_post_init__(self):
        self.uniqid = hash(self.old_path)

    def __eq__(self, other):
        return self.uniqid == other.uniqid

    def __hash__(self):
        return self.uniqid

    def do_move(self):
        """Complete the move operation.

        We expect the destination path to exist (much like regular mv) as
        this helps the end user avoid mistakes.
        """
        # if not self.new_path.parent.exists():
        #    self.new_path.parent.mkdir(exist_ok=True, parents=True)
        self.old_path.rename(self.new_path)


@define  # (frozen=True)
class Sample(object):
    """represents a sample file.

    Attributes:
        path (Path): Path object for the sample file.
        settings (list[SampleSetting]): list of SampleSettings for this sample
    """

    path: Path
    settings: List['SampleSetting'] = field(factory=list, eq=False)

    def __eq__(self, other):
        return super(Sample, self).__eq__(other)

    def __hash__(self):
        return super(Sample, self).__hash__()


@define
class SampleSetting(object):
    """represents a sample in the context of a DelugeXML file.

    Attributes:
        xml_file (deluge_xml.DelugeXML): object for the XML file (song, kit or synth).
        xml_path (str): Xmlpath string locating the sample setting within the XML.
    """

    xml_file: 'deluge_xml.DelugeXML'
    sample: 'Sample'
    xml_path: str


@define
class ModOp(object):
    """Represents a successful modification operation.

    Attributes:
        operation: str
        path (str): file path
        instance (Any): modified instance.
    """

    operation: str
    path: str
    instance: object
