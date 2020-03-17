import tempfile

from guessit import guessit
import inflect
from loguru import logger
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
import srt

from usb.extract import Extractor
from usb.subtitle import Subtitles
from usb.utils import is_iterable, formatted_video


class VideoFile:
    def __init__(self, path):
        info = guessit(path)

        self.path = path
        self.show = info['title']
        self.title = info['episode_title']
        self.season = info['season']
        self.video = VideoFileClip(path, target_resolution=(360, 640), verbose=False)

        if is_iterable(info['episode']):
            self.episodes = info['episode']
        else:
            self.episodes = [info['episode']]


    @staticmethod
    def _generate_text(text):
        common = {
            "txt": text,
            "size": (600, 100),
            "method": 'caption',
            "font": 'Impact',
            "fontsize": 30,
            "align": "South"
        }

        txt_clip = TextClip(color='white', stroke_color='white', stroke_width=1, **common)
        txt_clip = txt_clip.set_pos((20,250))

        txt_bg = TextClip(color='black', stroke_color='black', stroke_width=5, **common)
        txt_bg = txt_bg.set_pos((20,250))

        return CompositeVideoClip([txt_bg, txt_clip], size=(720, 1280))


    def extract_subs(self):
        with tempfile.NamedTemporaryFile() as subfile:
            Extractor(self.path).extract(subfile.name)

            for subtitle in srt.parse(subfile.read().decode('utf-8')):
                yield subtitle


    def thumbnail(self, time, dest, text):
        text_clip = VideoFile._generate_text(text)
        text_clip.duration = self.video.duration

        video = CompositeVideoClip([self.video, text_clip])

        video.duration = self.video.duration

        try:
            video.save_frame(dest, t=(time + 1.0))
            logger.info('writing out thumbnail: {}', dest)
        except Exception as e:
            raise


    def __str__(self):
        return formatted_video(self.show, self.season, self.episodes)
