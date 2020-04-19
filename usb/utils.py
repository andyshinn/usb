import re
from typing import Iterable

import fsspec
import inflect

GLOB = "**/*.mkv"
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


def formatted_video(show, season, episodes):
    return "{} season {} {} {}".format(
        show, season, p.plural("episode", len(episodes)), p.join(episodes)
    )


def get_mkvs(path):
    return fsspec.open_files(path, auto_mkdirs=False)


def is_iterable(object):
    if isinstance(object, Iterable):
        return True

    return False


def msecs(start, end):
    return round((start + (end - start) / 2).total_seconds() * 1000)


def move_id(id, num):
    id_list = id.split("-")
    index = id_list[-1]
    next_index = str(int(index) + num)
    id_list.remove(index)
    id_list.append(next_index)
    id = "-".join(id_list)

    return id
