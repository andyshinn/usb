import re
from typing import Iterable
from pathlib import Path

import inflect

GLOB = '**/*.mkv'
REGEX_SEASON = r"(?:[Ss](\d{2}))"
REGEX_EPISODES = r"(?:[Ee](\d{2}))"

p = inflect.engine()


def parse_season(title):
    match = re.findall(REGEX_SEASON, title)

    if match:
        return int(match[0])

    return None


def parse_episodes(title):
    match = re.findall(REGEX_EPISODES, title)

    if match:
        return [int(i) for i in match]

    return None


def formatted_episodes(episodes):
    return "-".join(str(x) for x in episodes)


def get_mkvs(path):
    return Path(path).glob(GLOB)


def is_iterable(object):
    if isinstance(object, Iterable):
        return True

    return False


def msecs(start, end):
    return round((start + (end - start) / 2).total_seconds() * 1000)
