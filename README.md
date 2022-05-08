# deluge-card


[![pypi](https://img.shields.io/pypi/v/deluge-card.svg)](https://pypi.org/project/deluge-card/)
[![python](https://img.shields.io/pypi/pyversions/deluge-card.svg)](https://pypi.org/project/deluge-card/)
[![Build Status](https://github.com/mupaduw/deluge-card/actions/workflows/dev.yml/badge.svg)](https://github.com/mupaduw/deluge-card/actions/workflows/dev.yml)
[![codecov](https://codecov.io/gh/mupaduw/deluge-card/branch/main/graphs/badge.svg)](https://codecov.io/github/mupaduw/deluge-card)



A Python3 api for Synthstrom Audible Deluge SD cards.

* Documentation: <https://mupaduw.github.io/deluge-card>
* GitHub: <https://github.com/mupaduw/deluge-card>
* PyPI: <https://pypi.org/project/deluge-card/>
* Free software: MIT


## Features

* List sub-folders that resemble Deluge cards (DelugeCardFS).
* List contents of deluge filesystems (cards , folders).
* Get details of card contents: songs, samples, sample usage.
* Get song details like **tempo**, **key**, **scale**.
* Filter contents by paths, using posix **ls** glob patterns.
* Move samples like posix **mv**.
* Unit tested on Macosx, Linux & Windows, Python 3.8+.
* Song XML from fw3.15.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [waynerv/cookiecutter-pypackage](https://github.com/waynerv/cookiecutter-pypackage) project template.
