import logging
import logging.handlers
import sqlite3

import pendulum
import yaml


LOGGER = logging.getLogger('pso2_news')
LOGGER.setLevel(logging.DEBUG)

FH = logging.handlers.RotatingFileHandler(
    'news.log',
    maxBytes=4096,
    backupCount=5,
    )
FH.setLevel(logging.DEBUG)

CH = logging.StreamHandler()
CH.setLevel(logging.INFO)

FH.setFormatter(
    logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    )
CH.setFormatter(
    logging.Formatter(
        '%(levelname)s - %(message)s'
        )
    )

LOGGER.addHandler(FH)
LOGGER.addHandler(CH)

TODAY = pendulum.today()
NOW = pendulum.now()


DB = sqlite3.Connection('news.db')
CURSOR = DB.cursor()

SCHEMA = {
    'UQ': '(DATE TEXT UNIQUE, NAME TEXT, TITLE TEXT, URL TEXT)'
    }

for table, schema in SCHEMA.items():
    CURSOR.execute('CREATE TABLE IF NOT EXISTS {0} {1}'.format(table, schema))
    DB.commit()


CURSOR.execute('SELECT * FROM UQ')
RESULTS = sorted(CURSOR.fetchall(), reverse=True)


try:
    with open('main.yaml', 'r') as f:
        yaml.safe_load(f)['FIRST_RUN']
        FIRST_RUN = False
except (FileNotFoundError, KeyError, TypeError):
    FIRST_RUN = True
    LOGGER.info(
        'This is a first run. '
        'A first run will make subtle changes to the year of UQs.'
        )

with open('blacklist.yaml', 'r') as f:
    BLACKLIST = yaml.safe_load(f)

try:
    UQ_BLACKLIST = BLACKLIST['uq']
except (KeyError, TypeError):
    UQ_BLACKLIST = []
    LOGGER.warning('The blacklist is malformed. Please download a new copy.')


def write_main() -> None:
    """Write main configuration yaml.

    Currently, main.yaml should only include a "FIRST_RUN" element.

    """
    if FIRST_RUN:
        with open('main.yaml', 'w') as f:
            yaml.safe_dump({'FIRST_RUN': False})
