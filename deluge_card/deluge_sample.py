"""Main classes representing Deluge Sample."""

from pathlib import Path
from typing import Iterator, List

from attrs import define, field


def mv_samples(samples: Iterator['Sample'], pattern: str, dest: Path) -> Iterator['Sample']:
    """Modify sample paths just as posix mv does."""

    def glob_match(sample):
        return Path(sample.path).match(pattern)

    def replace_path(sample):
        if dest.suffix == '':
            sample.path = Path(dest, sample.path.name)
        else:
            sample.path = dest
        return sample

    matching_samples = filter(glob_match, samples)
    return map(replace_path, matching_samples)


@define
class Sample(object):
    """represents a sample file.

    Attributes:
        path (Path): Path object for the sample file.
        settings (list[SampleSetting]): list of SampleSettings for this
    """

    path: Path
    settings: List['SampleSetting'] = field(factory=list, eq=False)


if False:
    # for forward-reference type-checking:
    # ref https://stackoverflow.com/a/38962160
    import deluge_song


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
