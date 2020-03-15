import tempfile

import cv2
from guessit import guessit
import inflect
from loguru import logger
import srt

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
        self.video = cv2.VideoCapture(str(path))

        if is_iterable(info['episode']):
            self.episodes = info['episode']
        else:
            self.episodes = [info['episode']]


    def _write_image_text(self, dest, image, text):
        font                   = cv2.FONT_HERSHEY_SIMPLEX
        fontScale              = 1.5
        white                  = (255, 255, 255)
        black                  = (0, 0, 0)
        thickness              = 4

        y0, dy = 100, 50
        for i, line in enumerate(text.split('\n')):
            y = y0 + i*dy

            cv2.putText(image, line,
                (y0, y),
                font,
                fontScale,
                black,
                thickness+8)
            cv2.putText(image, line,
                (y0, y),
                font,
                fontScale,
                white,
                thickness)

        return cv2.imwrite(dest, image)


    def extract_subs(self):
        with tempfile.NamedTemporaryFile() as subfile:
            Extractor(self.path).extract(subfile.name)

            for subtitle in srt.parse(subfile.read().decode('utf-8')):
                yield subtitle


    def thumbnail(self, msec, dest, text):
        self.video.set(cv2.CAP_PROP_POS_MSEC, int(msec))
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
            p.plural("episode", len(self.episodes)),
            p.join(self.episodes)
        )
