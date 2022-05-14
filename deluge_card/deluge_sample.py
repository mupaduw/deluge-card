"""Main classes representing Deluge Sample."""

import itertools
from pathlib import Path
from typing import Iterator, List

from attrs import define, field

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    import deluge_kit
    import deluge_song
    import deluge_synth
    import deluge_xml

    import deluge_card


def all_used_samples(card: 'deluge_card.DelugeCardFS', pattern: str = '') -> Iterator['Sample']:
    """Get all samples referenced in XML files."""
    return itertools.chain(
        map(lambda synth: synth.samples(pattern), card.synths()),
        map(lambda sng: sng.samples(pattern), card.songs()),
        map(lambda kit: kit.samples(pattern), card.kits()),
    )


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
        sample.path = move_op.new_path.relative_to(root)
        return move_op

    matching_samples = filter(glob_match, samples)
    return map(build_move_op, matching_samples)


def modify_sample_songs(samples: Iterator['Sample']) -> Iterator['deluge_song.DelugeSong']:
    """Update song XML elements."""

    def update_song_elements(sample):
        # print(f"DEBUG update_song_elements: {sample}")
        for setting in sample.settings:
            if not setting.xml_path[:6] == '/song/':
                continue
            print(f"DEBUG update_song_elements setting: {setting}")
            setting.xml_file.update_sample_element(setting)
            yield setting.xml_file

    return itertools.chain.from_iterable(map(update_song_elements, samples))


def modify_sample_kits(samples: Iterator['Sample']) -> Iterator['deluge_kit.DelugeKit']:
    """Update kit XML elements."""

    def update_kit_elements(sample):
        for setting in sample.settings:
            if not setting.xml_path[:5] == '/kit/':
                continue
            print(f"DEBUG update_kit_elements setting: {setting}")
            setting.xml_file.update_sample_element(setting)
            yield setting.xml_file

    return itertools.chain.from_iterable(map(update_kit_elements, samples))


def modify_sample_synths(samples: Iterator['Sample']) -> Iterator['deluge_synth.DelugeSynth']:
    """Update synth XML elements."""

    def update_synth_elements(sample):
        for setting in sample.settings:
            if not setting.xml_path[:7] == '/sound/':
                continue
            print(f"DEBUG update_synth_elements setting: {setting}")
            setting.xml_file.update_sample_element(setting)
            yield setting.xml_file

    return itertools.chain.from_iterable(map(update_synth_elements, samples))


def ensure_absolute(root: Path, dest: Path):
    """Make sure the path is absolute, if not make it relate to the root folder."""
    return dest if dest.is_absolute() else Path(root, dest)


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

    sample_move_ops = list(modify_sample_paths(root, samples, pattern, dest))  # do materialise the list

    updated_songs = set(modify_sample_songs(map(lambda mo: mo.sample, sample_move_ops)))
    updated_kits = set(modify_sample_kits(map(lambda mo: mo.sample, sample_move_ops)))
    updated_synths = set(modify_sample_synths(map(lambda mo: mo.sample, sample_move_ops)))

    # write the modified XML, per unique song
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


@define  # (eq=False)  # frozen abuse!
class Sample(object):
    """represents a sample file.

    Attributes:
        path (Path): Path object for the sample file.
        settings (list[SampleSetting]): list of SampleSettings for this sample
    """

    path: Path
    settings: List['SampleSetting'] = field(factory=list, eq=False)


@define
class SampleSetting(object):
    """represents a sample in the context of a DelugeXML file.

    Attributes:
        xml_file (deluge_xml.DelugeXML): object for the XML file (song, kit or synth).
        xml_path (str): Xmlpath string locating the sample setting within the XML.
    """

    xml_file: 'deluge_xml.DelugeXML'  # noqa (for F821 undefined name)
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
