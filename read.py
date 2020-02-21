import json
import os
import glob
import re

import srt
from cv2 import imwrite, VideoCapture, CAP_PROP_POS_MSEC
from elastic_app_search import Client
from loguru import logger

FILE_JSON = "json/{}.json"
FILE_VIDEO = "videos/{}.mkv"
VIDEO = False
INDEX = True
EP_REGEX = '^(s\\d{2})((?:e\\d{2})+)$'
API_KEY = 'private-2dp5rm5rrn4tfqii3v262c8p'


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def msecs(start, end):
    return ((start + (end - start) / 2).total_seconds() * 1000)


def serialized_subtitle(subtitle, season, episode, image):
    return {
        "id": "seinfeld-{}{}-{}".format(season, episode, subtitle.index),
        "episode": episode,
        "season": season,
        "index": subtitle.index,
        "start": str(subtitle.start),
        "end": str(subtitle.end),
        "milliseconds_middle": msecs(subtitle.start, subtitle.end),
        "content": subtitle.content,
        "preview": image,
    }


def parse_subtitles(path="subs/*.srt"):
    subtitles = []

    with open(path, 'r') as file:
        parsed_subtitles = list(srt.parse(file.read()))


client = Client(
    base_endpoint='localhost:3002/api/as/v1',
    api_key=API_KEY,
    use_https=False,
)

for file in glob.glob("subs/*.srt"):
    with open(file, 'r') as subtitle_file:
        parsed_subtitles = list(srt.parse(subtitle_file.read()))
        fname = os.path.splitext(os.path.basename(file))[0]
        season = re.match(EP_REGEX, fname).group(1)
        episode = re.match(EP_REGEX, fname).group(2)

        logger.info("indexing episode {}{}", season, episode)

        if VIDEO:
            video = VideoCapture(FILE_VIDEO.format(fname))

        subtitles = []

        for subtitle in parsed_subtitles:
            offset = msecs(subtitle.start, subtitle.end)
            image_name = 'previews/{}_{}.jpg'.format(fname, subtitle.index)

            if VIDEO:
                video.set(CAP_PROP_POS_MSEC, subtitle.start.total_seconds() * 1000)
                success, image = video.retrieve()

                if success:
                    imwrite(image_name, image)

            document = serialized_subtitle(subtitle, season, episode, image_name)
            subtitles.append(document)

        if INDEX:
            for chunk in chunks(subtitles, 100):
                client.index_documents('usb', chunk)

            with open(FILE_JSON.format(episode), 'w') as file:
                file.write(json.dumps(subtitles))
