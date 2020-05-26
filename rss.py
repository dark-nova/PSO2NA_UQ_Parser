from datetime import timedelta

import pendulum
from feedgen.feed import FeedGenerator

import config


AUTHOR = {'name': 'SEGA'}


class UQRSS:
    """RSS feed for Urgent Quests."""

    PRIOR_MINS = timedelta(minutes=30)
    EVENT_TIME = str(config.NOW + PRIOR_MINS)

    def __init__(self) -> None:
        """Initialize the RSS generation first by initializing feedgen."""
        self.fg = FeedGenerator()
        self.fg.title('PSO2 News: Urgent Quests')
        self.fg.author(AUTHOR)
        self.fg.description('Phantasy Star Online 2 News tracker for the West')
        self.fg.link(
            href='https://pso2.com/news/urgent-quests',
            rel='alternate',
            )
        self.fg.link(
            href='https://dark-nova.me/pso2/uq.xml',
            rel='self',
            )
        self.fg.language('en-US')

    def generate_feed(self) -> None:
        """Generate a feed by going through the database."""
        config.CURSOR.execute('SELECT * FROM UQ')
        results = sorted(config.CURSOR.fetchall(), reverse=True)
        start = 0
        for n, (dt_str, uq, title, url) in enumerate(results):
            if dt_str > self.EVENT_TIME:
                continue
            elif start == 0:
                start = n
            elif n - start > 10:
                return
            entry = self.fg.add_entry()
            entry.title(uq)
            entry.author(AUTHOR)
            #entry.description(uq)
            entry.link(href=url)
            entry.guid(url)
            entry.pubDate(pendulum.parse(dt_str))

    def write_feed(self) -> None:
        """Write out the feed after generating entries."""
        if len(self.fg.entry()) > 0:
            self.fg.rss_file('uq.xml')
        else:
            config.LOGGER.error('No entries were generated!')


if __name__ == '__main__':
    uq = UQRSS()
    uq.generate_feed()
    uq.write_feed()

