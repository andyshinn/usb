import tempfile

import cv2
from guessit import guessit
import inflect
from loguru import logger

from usb.extract import Extractor
from usb.subtitle import Subtitles
from usb.utils import is_iterable

p = inflect.engine()


class VideoFile:
    def __init__(self, path):
        info = guessit(path)

        self.path = path
        self.show = info['title']
        self.title = info['episode_title']
        self.season = info['season']
        self.video = cv2.VideoCapture(path)

        if is_iterable(info['episode']):
            self.episode = info['episode']
        else:
            self.episode = [info['episode']]


    def _write_image_text(self, dest, image, text):
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        fontScale              = 1.5
        fontColor              = (255,255,255)
        thickness               = 3

        y0, dy = 100, 50
        for i, line in enumerate(text.split('\n')):
            y = y0 + i*dy

            cv2.putText(image, line,
                (y0, y),
                font,
                fontScale,
                fontColor,
                thickness)

        return cv2.imwrite(dest, image)


    def extract_subs(self):
        subtitles = []

        with tempfile.NamedTemporaryFile() as subfile:
            Extractor(self.path).extract(subfile.name)

            for subtitle in Subtitles(subfile).list:
                subtitles.append(subtitle)

        return subtitles


    def thumbnail(self, msec, dest, text):
        self.video.set(cv2.CAP_PROP_POS_MSEC, msec)
        success, image = self.video.retrieve()

        if success:
            logger.info('writing out thumbnail: {}', dest)
            success = self._write_image_text(dest, image, text)

            if not success:
                logger.info('failed writing thumbnail: {}', dest)
        else:
            logger.info('failed to capture frame from video: {}', self.path)


    def __str__(self):
        return "{} season {} {} {}".format(
            self.show,
            self.season,
            p.plural("episode", len(self.episode)),
            p.join(self.episode)
        )
