"""Main classes representing Deluge Sample."""

from pathlib import Path
from typing import Iterator, List, Set

from attrs import define, field

if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    from itertools import chain

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


def modify_sample_songs(move_ops: Iterator['SampleMoveOperation']) -> Set['deluge_song.DelugeSong']:
    '''Update song XML'''

    def update_song_elements(move_op):
        for setting in move_op.sample.settings:
            elem = setting.song.update_sample_element(setting)
            assert elem.get('fileName') == str(setting.sample.path)
            yield setting.song

    return set(chain(map(update_song_elements, move_ops)))


def mv_samples(samples: Iterator['Sample'], pattern: str, dest: Path):

    sample_move_ops = modify_sample_paths(samples, pattern, dest)
    updated_songs = modify_sample_songs(sample_move_ops)

    print("sample_move_ops")
    print(sample_move_ops)
    print("Song updates")
    print(updated_songs)
    # write the modified XML
    # map(lambda song: DelugeSong.write_xml(song), updated_songs)


@define
class SampleMoveOperation(object):
    """represents a sample file move operation.

    Attributes:
        old_path (Path): original Path.
        new_path (Path): new Path.
        sample (Sample): sample instance.
    """

    old_path: Path
    new_path: Path
    sample: 'Sample'


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
