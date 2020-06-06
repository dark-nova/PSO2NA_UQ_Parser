# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.1] - 2020-06-05
### Changed
- Instead of stopping parsing in `MainPage.parse()`, continue to parse, only ignoring existing entries. (They will be skipped.)

### Fixed
- Fixed incorrect reference to `UQMainPage` (see 1.0.0) in [main.py](main.py).
- Fixed `self.schedules` not being `self.schedules.items()` in [uq.py](uq.py).

## [1.1.0] - 2020-06-04
### Added
- Added a new function `MainPage.delete_old()` in [uq.py](uq.py) that deletes schedules (and their associated UQs) if the schedule is no longer found on the main page. This is run in [main.py](main.py). Note that if `MainPage.parse()` is not called prior, `delete_old()` *will* error.

### Changed
- Uncommented a `+ 1` to `parse_date()` in [uq.py](uq.py) for years. The +1 is meant for incrementing year for future events in the new year. e.g. the script is run in December and found a new schedule in January. The year will be bumped up based on months (`12` and  `1` respectively). If results have not been cached or updated, comment out the `+ 1`.
- Webhooks are now generic, no longer tied to *Discord*, as long as the method is `POST`. Consequently, this means you should use the full URL in the configuration, not just the ID.

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
