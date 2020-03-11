import re
import glob
from typing import Iterable

import inflect


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


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def get_files(path):
    return glob.glob(path)


def is_iterable(object):
    if isinstance(object, Iterable):
        return True

    return False

# 
# def english_season_episode(guess):
#     ep = "Season {} {} {}".format(
#         guess['season'],
#         p.plural("episode", len(slist(guess['episode']))),
#         p.join(slist(guess['episode']))
#     )
#
#     return ep
