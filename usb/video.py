import tempfile
from typing import Iterator

from guessit import guessit
from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
import srt

from usb.logging import logger
from usb.extract import Extractor
from usb.utils import is_iterable


IGNORE_EPISODES = {"Seinfeld": {6: [14, 15], 9: [21, 22]}}


class InfoMixin:
    def __init__(self, path):
        self.__dict__.update(guessit(path))


class VideoFile(InfoMixin):
    def __init__(self, path):
        self.episode_title = None
        self.path = path
        self.season = None
        self.show = None
        self.title = None
        self.video_clip = VideoFileClip(path, target_resolution=(360, 640), verbose=False)
        super(VideoFile, self).__init__(path)

        if not is_iterable(self.episode):
            self.episode = [self.episode]

    @property
    def ignored(self):
        ignored_show = IGNORE_EPISODES.get(self.title)
        if ignored_show:
            if self.season in ignored_show:
                return all(ep in self.episode for ep in ignored_show.get(self.season))
        return False

    @staticmethod
    def _generate_text(text):
        common = {
            "txt": text,
            "size": (600, 100),
            "method": "caption",
            "font": "Impact",
            "fontsize": 30,
            "align": "South",
        }

        txt_clip = TextClip(color="white", stroke_color="white", stroke_width=1, **common)
        txt_clip = txt_clip.set_pos((20, 250))

        txt_bg = TextClip(color="black", stroke_color="black", stroke_width=5, **common)
        txt_bg = txt_bg.set_pos((20, 250))

        return CompositeVideoClip([txt_bg, txt_clip], size=(720, 1280))

    def extract_subs(self) -> Iterator[srt.Subtitle]:
        with tempfile.NamedTemporaryFile() as subfile:
            Extractor(self.path).extract(subfile.name)

            yield from srt.parse(subfile.read().decode("utf-8"))

    def thumbnail(self, time, dest, text):
        text_clip = VideoFile._generate_text(text)
        text_clip.duration = self.video_clip.duration
        video = CompositeVideoClip([self.video_clip, text_clip])
        video.duration = self.video_clip.duration

        try:
            video.save_frame(dest, t=(time + 1.0))
            logger.info("writing out thumbnail: {}", dest)
        except ValueError:
            logger.opt(exception=True).debug("Exception logged with debug level:")
