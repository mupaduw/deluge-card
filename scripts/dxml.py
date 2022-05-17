"""Read a deluge xml file and write it out again."""

import argparse
from pathlib import Path

from deluge_card import list_deluge_fs
from deluge_card.deluge_xml import DelugeXml


def main():
    """Main entrypoint."""
    parser = argparse.ArgumentParser(description='dxml.py - rewrite deluge XML via DelugeXML class.')

    parser.add_argument('root', help='root folder, must be a valid Deluge file system.')
    parser.add_argument('input', help='XML file to read, relative to root')
    parser.add_argument('output', help='XML file to write')
    parser.add_argument('-D', '--debug', action="store_true", help="print debug statements")

    args = parser.parse_args()

    card_imgs = list(list_deluge_fs(args.root))

    if len(card_imgs) == 0:
        print('No card found.')
        return
    if len(card_imgs) > 1:
        print("multiple cards found, only single card mv is supported.")
        return

    card = card_imgs[0]
    assert Path(args.input).exists()
    xml_file = DelugeXml(card, Path(args.input))
    xml_file.write_xml(new_path=Path(args.output))


if __name__ == '__main__':
    main()  # pragma: no cover
