# Usage

To use deluge-card in a project

```
import deluge_card
```

## list cards and their songs:
```
from deluge_card import list_deluge_fs

for card in list_deluge_fs('/deluge_cards/root_folder'):
	print(f'card at {card.path}'')

	# list the songs on the card
	for song in card.songs():
		print(song, song.tempo(), song.key())

```

## list samples and usage:
```
from deluge_card import DelugeCardFS

card = DelugeCardFS('path/to/my/card')
# list the samples on the card
for samples in card.samples():
	songs = set([s.song for s in sample.settings()])
	usage = list(sample.settings)
	print(sample, "used in", len(usage), "settings, in", len(songs), "songs.")

```

## move samples
```
card = DelugeCardFS('path/to/my/card')
for update_operation in card.mv_samples("**/Kick*.wav", Path('SAMPLES/Moved')):
	print(update_operation)
```
