# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.6.0] - 2022-05-19
### Added
 - mv_samples method on DelugeCardFS for top-level API.
### Changed
 - updated usage to show move example
 - refactored samples listing to deluge_card module

## [0.5.0] - 2022-05-18

### Added
 - handle recursive paths for SONG, KIT, SYNTH folders for firmware 4.0+
 - mv_samples handles KITS
 - mv_samples handles SYNTHS
 - drop illegal XML elements
 - more test coverage
 - local dev scripts for XML validation and manual tests

## [0.4.2] - 2022-05-12
### Changed
 - fix issue [12](https://github.com/mupaduw/deluge-card/issues/12) file not found
 - improve reporting

## [0.4.1] - 2022-05-11
### Changed
 - fix path logic and validation; add validation tests;
 - improve test cover
 - make error tests OS independent;

## [0.4.0] - 2022-05-11
### Added
 - new mv_samples method.
 - new validate_mv_dest method.
 - more usage examples.
 - simple scripts/dmv.py script for testing.
 - more typing.
 - new DelugeCardFS.from_folder() static method.
 - list of features in README.

### Changed
 - using attrs, some methods are now attributes.
 - root_note, scale changes.
 - improving docstrings.

## [0.3.0] - 2022-05-03
### Added
 - Posix glob-style filename matching for songs, samples, song_samples.

## [0.2.3] - 2022-05-02
### Changed
- Removed dev-requirements from the published package.

## [0.2.2] - 2022-05-01
###Added
- read song & sample basics
- deluge filesystem basics

## [0.1.1-alpha1] - 2022-04-30
### Changed
- tagged release for doc publication

## [0.1.0] - 2022-04-30
### Changed
- First release on PyPI.
