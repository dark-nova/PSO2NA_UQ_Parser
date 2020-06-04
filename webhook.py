from datetime import timedelta
from typing import Dict

import pendulum
import requests
import yaml

import config


NEXT = config.NOW + timedelta(minutes=30)

MESSAGE = """
Time: **{0}** (less than 30 minutes)

ᴿᵉᵃᵈ ᵗʰᵉ [ˢᶜʰᵉᵈᵘˡᵉ]({1})
"""

with open('webhook.yaml', 'r') as f:
    CONF = yaml.safe_load(f)
    ID = CONF['ID']
    try:
        LAST = CONF['LAST']
    except KeyError:
        LAST = None


def execute_webhook(dt: pendulum.datetime, uq: str, title: str) -> None:
    """Execute webhook given a UQ's name, datetime, and title of the
    event page it belongs.

    Args:
        dt (pendulum.datetime): the datetime of the UQ
        uq (str): name of the UQ
        title (str): title of the page that had the UQ on schedule

    """
    payload = {
        "embeds": [
            {
                "title": f"**{uq}**",
                "description": MESSAGE.format(
                    dt.to_day_datetime_string(),
                    title,
                    )
                }
            ]
        }
    response = requests.post(ID, json=payload)
    out = {
        'ID': ID,
        'LAST': LAST,
        }
    with open('webhook.yaml', 'w') as f:
        yaml.safe_dump(out, stream=f)

    config.LOGGER.info(f'Executed webhook @ {config.NOW}: {response}')
    config.LOGGER.info(f'UQ: {uq}, DT: {dt}')



def search_events() -> None:
    """Search events by going through the database, finding one that
    will happen between now (to be run at :00 and :30) and 30 minutes
    later.

    """
    if LAST:
        dt_strs = [dt_str for dt_str, uq, title, url in config.RESULTS]
        index = dt_strs.index(LAST)
        dt_str, uq, title, url = config.RESULTS[index - 1]
        dt = pendulum.parse(dt_str)
        if config.NOW <= dt <= NEXT:
            execute_webhook(dt, uq, url)
            return
    else:
        for dt_str, uq, title, url in config.RESULTS:
            dt = pendulum.parse(dt_str)
            # In reverse chronological order, some events may be ahead.
            # Those events should be ignored.
            if dt > NEXT:
                continue
            # Likewise, some events will be behind. If an event hasn't
            # been found in range (they cannot have collisions),
            # stop looking.
            elif dt < config.NOW:
                return
            else:
                execute_webhook(dt, uq, url)
                return


if __name__ == '__main__':
    search_events()
