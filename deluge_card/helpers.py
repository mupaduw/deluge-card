"""Helper functions."""
from pathlib import Path


def ensure_absolute(root: Path, dest: Path):
    """Make sure the path is absolute, if not make it relate to the root folder."""
    return dest if dest.is_absolute() else Path(root, dest)
