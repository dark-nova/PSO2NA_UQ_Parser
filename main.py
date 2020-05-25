import re
from typing import Dict, List, Tuple

import pendulum
import requests
from bs4 import BeautifulSoup, Tag
from more_itertools import grouper


example_main = 'example-urgent_quests.html'
example_scheds = [
    '2020-02',
    #'2020-03',
    #'2020-05_3',
    #'about',
    ]

today = pendulum.today()


MONTHS = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
    ]

N = re.compile(r'[0-9]+')
TIME = re.compile(r'[0-9]{1,2}:[0-9][0-9]([ap]m)?', re.I)
AMPM = re.compile(r'[ap]m', re.I)

NOT_UQ = [
    "Server Maintenance (Users won't be able to log in)",
    "Servers Open (Start of Extended Period)",
    "Server Shutdown (End of the Closed Beta Test)",
    ]


def open_example_uq_sched(schedule: str) -> BeautifulSoup:
    with open(f'example-urgent_quest-{schedule}.html', 'r') as example:
        soup = BeautifulSoup(example, 'html.parser')
    return soup


def parse_date(month: int, day: int) -> Tuple[int, int, int]:
    """Parse a date given month and day only and convert to
    a tuple."""
    if month < today.month:
        year = today.year #+ 1
    else:
        year = today.year
    return year, month, day


def parse_special_date(date: str) -> pendulum.datetime:
    """Parse a date like "February 8th" into pendulum.datetime."""
    month, day = date.split(' ')[:2]
    month = MONTHS.index(month) + 1
    day = int(N.search(day).group(0))
    return parse_date(month, day)


def parse_time(time: str) -> Tuple[int, int]:
    """Parse time like "0:00 - 0:30am" and retrieve the time in 24h."""
    start, end = [TIME.search(t).group(0) for t in time.split(' – ')]
    hour, minute = [int(n) for n in start.split(':')]
    hour %= 12
    ampm = AMPM.search(end).group(0)
    if ampm == 'pm':
        hour += 12
    return hour, minute


def is_not_uq(uq: str) -> bool:
    """Is the UQ actually not a UQ? Filter by name here."""
    return uq in NOT_UQ


def parse_only_tables(tables: List[Tag]) -> Dict[pendulum.datetime, str]:
    """Parse a table, ignoring any color code. Used in 2020-02.

    Args:
        tables (List[Tag]): a list of html tables; tables here are
            2-columns wide, with time ranges in column 1 and UQ name
            in column 2

    Returns:
        Dict[pendulum.datetime, str]: a dictionary with keys that
            correspond to time and values being the UQ name at the time

    """
    schedule = {}
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
            hour, minute = parse_time(time)
            dt = pendulum.datetime(year, month, day, hour, minute)
            schedule[dt] = uq
    return schedule


def parse_uq_sched(soup: BeautifulSoup):
    schedule = {}
    tables = soup.find('div', 'emergency cms')
    for table_a, table_b in grouper(tables.find_all('table'), 2):
        rows = table_a.find_all('tr')
        cols = rows[0].find_all('td')
        if len(cols) == 1:
            rows.pop(0)
            cols = rows[0].find_all('td')
        # Special case: example-urgent_quest-2020-02.html
        if len(cols) == 2:
            # Because 2020-02 does not have a color code per table,
            # iterate over both tables instead.
            return parse_only_tables([table_a, table_b])
        else:
            dates = [
                parse_date(*[int(n) for n in col.text.split('/')])
                for col in cols[1:]
                ]
            # Skip the 2nd row (days of the week) and 3rd row ("Time (PDT)").
            for row in rows[3:]:
                print(row)

    return schedule


if __name__ == '__main__':
    for schedule in example_scheds:
        soup = open_example_uq_sched(schedule)
        print(parse_uq_sched(soup))
