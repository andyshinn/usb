import re

REGEX_SEASON = r"(?:[Ss](\d{2}))"
REGEX_EPISODES = r"(?:[Ee](\d{2}))"

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
