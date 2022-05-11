"""Main classes representing Deluge Sample."""

import itertools
import uuid
from pathlib import Path
from typing import Iterator, List, Set

from attrs import define, field

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    import deluge_song


def modify_sample_paths(
    root: Path, samples: Iterator['Sample'], pattern: str, dest: Path
) -> Iterator['SampleMoveOperation']:
    """Modify sample paths just as posix mv does."""

    def glob_match(sample) -> bool:
        return Path(sample.path).match(pattern)

    def replace_path(sample) -> SampleMoveOperation:
        if dest.suffix == '':
            move_op = SampleMoveOperation(ensure_absolute(root, sample.path), Path(dest, sample.path.name), sample)
        else:
            move_op = SampleMoveOperation(ensure_absolute(root, sample.path), Path(dest), sample)
        sample.path = move_op.new_path.relative_to(root)
        return move_op

    matching_samples = filter(glob_match, samples)
    return set(map(replace_path, matching_samples))


def modify_sample_songs(samples: Iterator['Sample']) -> Set['deluge_song.DelugeSong']:
    """Update song XML elements."""

    def update_song_elements(sample):
        # print(f"DEBUG update_song_elements: {sample}")
        for setting in sample.settings:
            # print(f"DEBUG update_song_elements setting: {setting}")
            elem = setting.song.update_sample_element(setting)
            assert elem.get('fileName') == str(setting.sample.path)
            yield setting.song

    return set(itertools.chain.from_iterable(map(update_song_elements, samples)))


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
    """Move samples, updating any affected songs."""
    # print('DEBUG', root, pattern, dest)

    dest = ensure_absolute(root, dest)
    validate_mv_dest(root, dest)  # raises exception if args are invalid

    sample_move_ops = list(modify_sample_paths(root, samples, pattern, dest))  # do materialise the list
    updated_songs = list(modify_sample_songs(map(lambda mo: mo.sample, sample_move_ops)))

    # write the modified XML
    for song in updated_songs:
        song.write_xml()

    for move_op in sample_move_ops:
        move_op.do_move()
        yield move_op


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
    uniqid: uuid.uuid4 = field(init=False)

    def __attrs_post_init__(self):
        self.uniqid = hash(uuid.uuid4())

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


@define(eq=False)  # frozen abuse!
class Sample(object):
    """represents a sample file.

    Attributes:
        path (Path): Path object for the sample file.
        settings (list[SampleSetting]): list of SampleSettings for this sample
    """

    path: Path
    settings: List['SampleSetting'] = field(factory=list, eq=False)
    # uniqid: uuid.uuid4 = field(init=False)

    # def __attrs_post_init__(self):
    #     self.uniqid = hash(uuid.uuid4())

    # def __eq__(self, other):
    #     return self.uniqid == other.uniqid

    # def __hash__(self):
    #     return self.uniqid

    def __eq__(self, other):
        return self.path == other.path

    def __hash__(self):
        return hash(self.path)


@define
class SampleSetting(object):
    """represents a sample in the context of a DelugeSong.

    Attributes:
        song_path (Path): Path object for the XML song file.
        xml_path (str): Xmlpath string locating the sample setting within the XML.
    """

    song: 'deluge_song.DelugeSong'  # noqa (for F821 undefined name)
    sample: 'Sample'
    xml_path: str