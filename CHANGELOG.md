# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.3] - 2020-06-19
### Changed
- In [uq.py](uq.py):
    - Renamed `hexcolor` in `get_uq_from_cell` to `color`, as the color can be a hard-coded string (e.g. `red`) or a hex representation.
    - Renamed `get_colors_from_table()` to `get_colors_from_key()`, as `key` is a more accurate descriptor of the HTML table.
    - Instead of relying on hard-coded colors, a new function `get_closest_color()` was added: this should get the correct UQ if colors don't match exactly between the schedule and the color key.

## [1.1.2] - 2020-06-10
### Changed
- In [uq.py](uq.py):
    - `parse_date()` now considers cases where a schedule contains an event in the past year (e.g. December) posted in the new year (e.g. January).
    - Combine `MainPage.delete_old()` with `MainPage.parse()` since `delete_old()` required `parse()` anyway.
- In [webhook.py](webhook.py):
    - Instead of only checking the direct next event, limit the results based on `LAST` known index.

### Fixed
- Added a specific check in `get_uq_from_cell()` for a hard-coded mismatch in colors (key and schedule colors differ).
- `webhook.execute_webhook()` should now update the `LAST` selected event.

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
