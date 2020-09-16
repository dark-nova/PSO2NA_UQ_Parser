# [PSO2NA][PSO2] UQ Parser

---

# This repo will be archived.

As of 2020-09-15, the new schedules are posted on Google Calendar, and the means to parse calendars in Google Calendar are not worth the effort to fix. Because of this change, this repo is no longer useful. For more information, see issue #3 (pinned). For historic reasons, the old README will continue below.

---

## Overview

This project scrapes from the [Urgent Quests main page](https://pso2.com/news/urgent-quests) to parse schedules into a database for easier reading. It works by going through the UQ main page and going through each schedule. If a schedule is not found in the database, meaning no entries in the database have the schedule's URL, the schedule is subsequently scraped for Urgent Quests.

Additionally, webhook and RSS functionality are included. They should be run separately from the main file and only after running the main script.

**Note that RSS functionality may be sunset and deprecated in the future.**

## Usage

Install dependencies, and run [main.py](main.py). Ideally, the script should be run once a day at midnight server time (i.e. `America/Los_Angeles`). **Do not create a `main.yaml`!** If you are running the project for the first time, let the project handle it.

Once you have at least the main script once, you can run [webhook.py](webhook.py) or [rss.py](rss.py). Like the main script, ideally these should run on a schedule, preferably every half hour (`:00` and `:30`).

## [Requirements](requirements.txt)

This code is designed around the following:

- Python 3.7+
    - `pendulum`
    - `pyyaml`
    - `requests`

## Disclaimer

This project is not affiliated with or endorsed by *[PSO2][PSO2]*, *[SEGA][SEGA]*, or *[Microsoft][MICROSOFT]*. See [LICENSE](LICENSE) for more detail.

[PSO2]: https://pso2.com/
[SEGA]: https://www.sega.com/
[MICROSOFT]: https://www.microsoft.com/
