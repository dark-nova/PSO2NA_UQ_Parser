import re
import sqlite3
from math import ceil
from time import sleep
from typing import Dict, List, Tuple, Union

import pendulum
import requests
from bs4 import BeautifulSoup, Tag
from more_itertools import grouper

import config


EXAMPLE_MAIN = 'example-urgent_quests.html'
EXAMPLE_SCHEDS = [
    '2020-02',
    '2020-03',
    '2020-05_1',
    '2020-05_3',
    'about',
    ]


MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
    ]

N = re.compile(r'[0-9]+')
RGB = re.compile(r'([0-9]+), ([0-9]+), ([0-9]+)')
TIME = re.compile(r'[0-9]{1,2}:[0-9][0-9]([ap]m)?', re.I)
AMPM = re.compile(r'[ap]m', re.I)

NOT_UQ = [
    "Server Maintenance (Users won't be able to log in)",
    "Servers Open (Start of Extended Period)",
    "Server Shutdown (End of the Closed Beta Test)",
    ]


def parse_date(month: int, day: int) -> Tuple[int, int, int]:
    """Parse a date given month and day only and convert to
    a tuple."""
    if month < config.TODAY.month:
        # Note that if you have not yet recorded/cached the current
        # records, you should comment out the +1. The +1 is only
        # meant to increment for future events that happen in
        # the new year.
        year = config.TODAY.year + 1
    elif month > config.TODAY.month:
        # I realized that on June 10th, 2020, the schedule for UQs was
        # posted June 10th but included June 9th (which had passed).
        # There is a distinct possibility that this will happen again,
        # when the schedule is posted on New Year's Day (around there)
        # and includes a day for December.
        year = config.TODAY.year - 1
    else:
        year = config.TODAY.year
    return year, month, day


def parse_special_date(date: str) -> pendulum.datetime:
    """Parse a date like "February 8th" into pendulum.datetime."""
    month, day = date.split(' ')[:2]
    month = MONTHS.index(month) + 1
    day = int(N.search(day).group(0))
    return parse_date(month, day)


def convert_time(time: str, ampm: str) -> Tuple[int, int]:
    """Convert time given "HH:MM" to 24h format."""
    hour, minute = [int(n) for n in time.split(':')]
    hour %= 12
    if ampm == 'pm':
        hour += 12
    return hour, minute


def parse_time(time: str) -> Tuple[int, int]:
    """Parse time like "1:00 AM" and convert."""
    time, ampm = time.split(' ')
    return convert_time(time, ampm.lower())


def parse_time_range(time: str) -> Tuple[int, int]:
    """Parse time like "0:00 - 0:30am" and convert."""
    start, end = [TIME.search(t).group(0) for t in time.split(' – ')]
    return convert_time(start, AMPM.search(end).group(0))


def is_not_uq(uq: str) -> bool:
    """Is the UQ actually not a UQ? Filter by name here."""
    return uq in NOT_UQ


def get_uq_from_cell(cell: Tag, colors: Dict[str, str]) -> Union[str, None]:
    """Get a UQ from a cell given the cell's color."""
    for attr in cell['style'].split(';'):
        if not attr:
            continue
        a, value = attr.split(':')
        if a == 'background':
            try:
                hexcolor = value.strip()
                return colors[hexcolor]
            except KeyError:
                # Another case of hard-coded colors, but incorrect.
                # Used for example-urgent_quest-2020-06_1.html;
                # Urgent Quest:  The Manifested Planetbreaker &
                #   The Chant to Cleanse the Calamity (60 minutes)
                # The key color is #341D8B while the schedule color is
                # 4F2CD0.
                if hexcolor == '#4F2CD0':
                    return colors['#341D8B']
                return


def get_hex_color_from_cell(cell: Tag) -> str:
    """Get a HEX color from the cell background, or if the background
    color is "red", just "red".

    Args:
        cell (Tag): a <td> element containing only a color

    """
    for attr in cell['style'].split(';'):
        if not attr:
            continue
        a, value = attr.split(':')
        if a == 'background':
            match = RGB.search(value)
            if match:
                rgb = '#' + ''.join(
                    [hex(int(n))[2:] for n in match.group(1, 2, 3)]
                    ).upper()
                return rgb
            else:
                # This is horrifying. Hard-coded colors.
                return value.strip()


def get_colors_from_table(table: Tag) -> Dict[str, str]:
    """Map a color from RGB to HEX to its UQ."""
    colors = {}
    for row in table.find_all('tr'):
        col_color, col_uq = row.find_all('td')
        color = get_hex_color_from_cell(col_color)
        colors[color] = col_uq.text.replace('\xa0', ' ')

    return colors


class Schedule:
    """Represents a schedule page for Urgent Quests."""

    def __init__(
        self, url_or_file: str, *, title: str = None, is_url: bool = True
        ) -> None:
        """Initialize the schedule parser with a URL or local file.

        Args:
            url_or_file (str): the URL or local file of a UQ schedule
            title (str, optional): the title of the schedule;
                defaults to None
            is_url (bool, optional): is url_or_file a URL?
                defaults to None

        """
        config.LOGGER.info(f'Initializing Schedule @ {url_or_file}')
        self.title = title
        self.is_url = is_url
        self.url = url_or_file
        if is_url:
            page = requests.get(url_or_file)
            self.soup = BeautifulSoup(page.text, 'html.parser')
        else:
            with open(f'example-urgent_quest-{schedule}.html', 'r') as example:
                self.soup = BeautifulSoup(example, 'html.parser')

    def parse(self) -> None:
        """Parse the page and convert into database entries."""
        self.schedule = {}
        tables = self.soup.find('div', 'emergency cms')
        for table_a, table_b in grouper(tables.find_all('table'), 2):
            rows = table_a.find_all('tr')
            cols = rows[0].find_all('td')
            width = float(cols[1]['width'].strip('%'))
            if len(cols) == 1:
                rows.pop(0)
                cols = rows[0].find_all('td')
            # Special case: example-urgent_quest-2020-02.html
            if len(cols) == 2:
                # Because 2020-02 does not have a color code per table,
                # iterate over both tables instead.
                self.parse_only_tables([table_a, table_b])
            else:
                dates = [
                    parse_date(*[int(n) for n in col.text.split('/')])
                    for col in cols[1:]
                    ]
                # Skip row 2 (days of the week) and row 3 ("Time (PDT)").
                color_map = get_colors_from_table(table_b)
                for row in rows[3:]:
                    widths = 0
                    try:
                        time = parse_time(row.find('td').text)
                    except ValueError:
                         # Some tables have empty rows under the table. Why.
                         continue
                    for cell in row.find_all('td')[1:]:
                        uq = get_uq_from_cell(cell, color_map)
                        widths += float(cell['width'].strip('%'))
                        if not uq:
                            continue
                        self.schedule[
                            pendulum.datetime(
                                *(dates[ceil(widths/width) - 1] + time),
                                tz='America/Los_Angeles'
                                )
                            ] = uq

        self.write_to_db()

    def parse_only_tables(self, tables: List[Tag]) -> None:
        """Parse a table, ignoring any color code. Used in 2020-02.

        Args:
            tables (List[Tag]): a list of html tables; tables here are
                2-columns wide, with time ranges in column 1 and UQ name
                in column 2

        """
        for table in tables:
            rows = table.find_all('tr')
            cols = rows[0].find_all('td')
            # Special case: 2nd table of example-urgent_quest-2020-02.html
            if len(cols) == 1:
                rows.pop(0)
                cols = rows[0].find_all('td')
            year, month, day = parse_special_date(
                table.previous_sibling.text
                )
            for row in rows[1:]:
                time, uq = [tag.text.strip() for tag in row.find_all('td')]
                # Special case:
                #   2nd table of example-urgent_quest-2020-02.html
                if time == 'Time (PST)':
                    continue
                if is_not_uq(uq):
                    continue
                hour, minute = parse_time_range(time)
                dt = pendulum.datetime(year, month, day, hour, minute)
                self.schedule[dt] = uq

    def write_to_db(self) -> None:
        """Write the schedule to DB."""
        config.CURSOR.execute('SELECT DATE FROM UQ')
        dates = config.CURSOR.fetchall()
        for date, uq in self.schedule.items():
            try:
                config.CURSOR.execute(
                    'INSERT INTO UQ VALUES (?, ?, ?, ?)',
                    (str(date), uq, self.title, self.url)
                    )
            except sqlite3.IntegrityError:
                # config.LOGGER.info(
                #     f'{date} (UQ: {uq}) was found in the DB! Skipped.'
                #     )
                continue

        if self.is_url:
            config.DB.commit()
        else:
            print('Example results:', self.schedule)


class MainPage:
    """Represents the main news page for Urgent Quests."""

    URL = 'https://pso2.com/news/urgent-quests'

    def __init__(self, is_url: bool = True) -> None:
        """Initialize main page for scraping.

        Args:
            is_url (bool, optional): are we using the real URL?
                defaults to None

        """
        config.LOGGER.info('Initializing MainPage...')
        self.is_url = is_url
        if is_url:
            page = requests.get(self.URL)
            self.soup = BeautifulSoup(page.text, 'html.parser')
        else:
            with open(EXAMPLE_MAIN, 'r') as example:
                self.soup = BeautifulSoup(example, 'html.parser')
        try:
            self.schedules = {result[2]: result[3] for result in config.RESULTS}
        except TypeError:
            self.schedules = None

    def parse(self) -> None:
        """Parse the page to find individual schedules."""
        self.new_schedules = {}
        news = self.soup.find('div', 'all-news-section')
        for schedule in news.find_all('div', 'content'):
            title = schedule.find('h3', 'title').text
            link = schedule.find('a', 'read-more')
            if not self.is_url:
                print('Example schedule title:', title)
                continue
            sched_link = link['onclick'].split("'")[1]
            url = f'{self.URL}/{sched_link}'
            self.new_schedules[title] = url
            if title in self.schedules and url == self.schedules[title]:
                config.LOGGER.info('Found a matching schedule; skipped.')
                config.LOGGER.info(f'- Match title: {title}')
                config.LOGGER.info(f'- Match URL:   {url}')
            else:
                sleep(10)
                s = Schedule(url, title=title)
                s.parse()

        if self.is_url:
            urls = self.new_schedules.values()
            for schedule, url in self.schedules.items():
                if url not in urls:
                    config.LOGGER.info('Deleting records from the following:')
                    config.LOGGER.info(f'- Title: {schedule}')
                    config.LOGGER.info(f'- URL: {url}')
                    config.CURSOR.execute(
                        'DELETE FROM UQ WHERE TITLE = ? AND URL = ?',
                        (schedule, url)
                        )
            config.DB.commit()


if __name__ == '__main__':
    for schedule in EXAMPLE_SCHEDS:
        s = Schedule(schedule, is_url=False)
        s.parse()
        sleep(2)
    mp = MainPage(is_url=False)
    mp.parse()
