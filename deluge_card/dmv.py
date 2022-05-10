"""Main dmv script."""

import argparse
from pathlib import Path

from deluge_sample import Sample, mv_samples

from deluge_card import list_deluge_fs


def list_samples(card, args):
    samples = list()
    if args.summary | args.verbose:
        print(f'Deluge filesystem {card} has {len(samples)} samples')
    if args.summary:
        return


def main():
    """Main entrypoint."""
    parser = argparse.ArgumentParser(description='dmv.py (dmv) - move FS contents')

    parser.add_argument('root', help='root folder to begin mv from')
    # parser.add_argument('type', help='one of of s=songs, a=samples, ss=song_samples (future: k=kits, i=instruments)')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-s", "--summary", help="summarise output", action="store_true")
    parser.add_argument('pattern', help='pattern')
    parser.add_argument('dest', help='pattern')
    parser.add_argument('-D', '--debug', action="store_true", help="print debug statements")

    args = parser.parse_args()
    if args.debug:
        print(f"Args: {args}")

    card_imgs = list(list_deluge_fs(args.root))
    if len(card_imgs) == 0:
        print('No card found.')
        return
    if len(card_imgs) > 1:
        print("multiple cards found, only single card mv is supported.")
        return

    card = card_imgs[0]
    samples = card.samples()
    new_path = Path(args.dest)

    for moved in mv_samples(card.card_root, samples, args.pattern, new_path):
        print(moved.new_path)


if __name__ == '__main__':
    main()  # pragma: no cover
