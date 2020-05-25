import logging
import logging.handlers
import sqlite3


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


DB = sqlite3.Connection('news.db')
CURSOR = DB.cursor()

SCHEMA = {
    'UQ': '(DATE TEXT UNIQUE, NAME TEXT)'
    }

for table, schema in SCHEMA.items():
    CURSOR.execute('CREATE TABLE IF NOT EXISTS {0} {1}'.format(table, schema))
    DB.commit()
