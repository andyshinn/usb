import os
import glob
import re

import srt
from elastic_app_search import Client
from loguru import logger

from usb.utils import parse_season, parse_episodes, chunks, formatted_episodes

API_KEY = 'private-ekzi3dcd8usuwtakwudttgcm'


def serialized_subtitle(subtitle, season, episodes, image):
    return {
        "id": "seinfeld-{}-{}-{}".format(season, formatted_episodes(episodes), subtitle.index),
        "episodes": episodes,
        "season": season,
        "index": subtitle.index,
        "start": str(subtitle.start),
        "end": str(subtitle.end),
        "content": subtitle.content,
        "preview": image,
    }

def index_subtitles(subtitles):
    client = Client(base_endpoint='appsearch:3002/api/as/v1', api_key=API_KEY ,use_https=False)

    for chunk in chunks(subtitles, 100):
        client.index_documents('usb', chunk)


def process_subtitles(path="subs/*.srt"):
    for file in get_subtitle_files(path):
        process_subtitle(file)


def get_subtitle_files(path):
    return glob.glob(path)


def index_subtitle(file):
    fname = os.path.splitext(os.path.basename(file))[0]
    season = parse_season(fname)
    episodes = parse_episodes(fname)

    logger.info("indexing episode {}{}", season, episodes)

    with open(file, 'r') as subtitle_file:
        subtitles = []
        parsed_subtitles = list(srt.parse(subtitle_file.read()))

        for subtitle in parsed_subtitles:
            image_name = '{}_{}.jpg'.format(fname, subtitle.index)
            document = serialized_subtitle(subtitle, season, episodes, image_name)
            subtitles.append(document)

        index_subtitles(subtitles)
