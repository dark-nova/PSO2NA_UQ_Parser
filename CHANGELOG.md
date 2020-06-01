# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2020-05-31
### Added
- Added *[Discord][DISCORD]* [webhook](webhook.py) support. Set this up by copying [webhook.yaml.example](webhook.yaml.example) to `webhook.yaml` and fill out the ID of the webhook. This project is not affiliated or endorsed by *[Discord][DISCORD]*.
- Added a check that ensures scraping only new schedules by getting the most recent entry and getting its schedule title.

### Changed
- In [uq.py](uq.py):
    - `UQMainPage` and `UQSchedule` were renamed `MainPage` and `Schedule`, respectively. The `UQ` is already implied with the module name.
- In [config.py](config.py):
    - The entire record of UQs is retrieved from the database. Formerly, `results` were used in [uq.py](uq.py) and [rss.py](rss.py). Currently, `rss.py` has not been updated. This point relates to the 2nd bullet point under "Added".

## [0.1.1] - 2020-05-25
### Fixed
- ~~Removed GUID per RSS entry, as the feed won't validate.~~ Just kidding, changed the value because RSS readers can't handle this.
- Added missing dependency `feedgen`.

## [0.1.0] - 2020-05-25
### Added
- Initial version

[DISCORD]: https://discord.com
