# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2020-05-31
### Added
- Added *[Discord][DISCORD]* [webhook](webhook.py) support. Set this up by copying [webhook.yaml.example](webhook.yaml.example) to `webhook.yaml` and fill out the ID of the webhook. This project is not affiliated or endorsed by *[Discord][DISCORD]*.

## [0.1.1] - 2020-05-25
### Fixed
- ~~Removed GUID per RSS entry, as the feed won't validate.~~ Just kidding, changed the value because RSS readers can't handle this.
- Added missing dependency `feedgen`.

## [0.1.0] - 2020-05-25
### Added
- Initial version

[DISCORD]: https://discord.com
