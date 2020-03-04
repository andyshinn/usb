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
REGEX_SEASON = r"(?:[Ss](\d{1,2}))"
REGEX_EPISODES = r"(?:[Ee](\d{2})+)"

EP_REGEX = '^(s\\d{2})((?:e\\d{2})+)$'
API_KEY = 'private-dw8nq5a2uqw1p97kn4mcadys'





def msecs(start, end):
    return ((start + (end - start) / 2).total_seconds() * 1000)




def parse_subtitles(path="subs/*.srt"):
    subtitles = []

    with open(path, 'r') as file:
        parsed_subtitles = list(srt.parse(file.read()))




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
