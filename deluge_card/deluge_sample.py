"""Main classes representing Deluge Sample."""

import itertools
from pathlib import Path
from typing import Iterator, List, Set

from attrs import define, field

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    import deluge_song


def modify_sample_paths(samples: Iterator['Sample'], pattern: str, dest: Path) -> Iterator['SampleMoveOperation']:
    """Modify sample paths just as posix mv does."""

    def glob_match(sample):
        return Path(sample.path).match(pattern)

    def replace_path(sample):
        if dest.suffix == '':
            move_op = SampleMoveOperation(Path(sample.path), Path(dest, sample.path.name), sample)
        else:
            move_op = SampleMoveOperation(Path(sample.path), Path(dest), sample)
        sample.path = move_op.new_path
        return move_op

    matching_samples = filter(glob_match, samples)
    return map(replace_path, matching_samples)


def modify_sample_songs(samples: Iterator['Sample']) -> Set['deluge_song.DelugeSong']:
    """Update song XML elements."""

    def update_song_elements(sample):
        for setting in sample.settings:
            elem = setting.song.update_sample_element(setting)
            assert elem.get('fileName') == str(setting.sample.path)
            yield setting.song

    return set(itertools.chain.from_iterable(map(update_song_elements, samples)))


def mv_samples(samples: Iterator['Sample'], pattern: str, dest: Path):
    """Move samples, updating any affected songs."""
    sample_move_ops = list(modify_sample_paths(samples, pattern, dest))
    updated_songs = list(modify_sample_songs([mo.sample for mo in sample_move_ops]))

    print("Song updates")
    print(updated_songs)
    # write the modified XML
    for song in updated_songs:
        song.write_xml()

    print("sample_move_ops")
    print(sample_move_ops)
    for move_op in sample_move_ops:
        move_op.do_move()


@define
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
    moved: bool = field(default=False)

    def do_move(self) -> bool:
        """Complete the move operation."""
        self.old_path.rename(self.new_path)
        self.moved = True
        return self.moved


@define
class Sample(object):
    """represents a sample file.

    Attributes:
        path (Path): Path object for the sample file.
        settings (list[SampleSetting]): list of SampleSettings for this
    """

    path: Path
    settings: List['SampleSetting'] = field(factory=list, eq=False)


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
