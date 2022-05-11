"""Main dmv script."""

import argparse
import itertools
from pathlib import Path

from deluge_card import list_deluge_fs
from deluge_card.deluge_sample import mv_samples, validate_mv_dest


def main():
    """Main entrypoint."""
    parser = argparse.ArgumentParser(description='dmv.py (dmv) - move FS contents')

    parser.add_argument('root', help='root folder, must be a valid Deluge file system.')
    parser.add_argument('pattern', help='glob pattern to match e.g. **/Clap*.wav')
    parser.add_argument('dest', help='target folder or file, which must be in a subfolder of root.')

    args = parser.parse_args()
    card_imgs = list(list_deluge_fs(args.root))

    if len(card_imgs) == 0:
        print('No card found.')
        return
    if len(card_imgs) > 1:
        print("multiple cards found, only single card mv is supported.")
        return

    card = card_imgs[0]
    song_samples = itertools.chain.from_iterable(map(lambda song: song.samples(), card.songs()))
    new_path = Path(args.dest)

    try:
        validate_mv_dest(card.card_root, Path(args.dest))
    except ValueError as err:
        print(err)
        return

    for moved in mv_samples(card.card_root, song_samples, args.pattern, new_path):
        print(moved.new_path)


if __name__ == '__main__':
    main()  # pragma: no cover
