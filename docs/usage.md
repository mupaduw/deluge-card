# Usage

To use deluge-card in a project

```
import deluge_card
```

## list cards, and songs available at folder:
```
from deluge_card import list_deluge_fs

for card in list_deluge_fs('/deluge_cards/root_folder'):
	print(f'card at {card.path}'')

	# list the songs on the card
	for song in card.songs():
		print(song, song.tempo(), song.key())

```

## list card samples and usage:
```
from deluge_card import DelugeCardFS

card = DelugeCardFS('path/to/my/card')
# list the samples on the card
for samples in card.samples():
	songs = set([s.song for s in sample.settings()])
	usage = len(list(sample.settings))
	print(sample, "used in", usage, "settings, in", len(songs), "songs.")

```
