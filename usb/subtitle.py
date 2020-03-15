
import re
import tempfile
from itertools import chain, islice

from srt import Subtitle
from elastic_app_search import Client
from loguru import logger

from usb.utils import formatted_episodes, msecs
from usb.search import Appsearch


class Document:
    def __init__(self, **kwargs):
        allowed_types = [str, int, list]

        self.__dict__.update((key, value) for key, value in kwargs.items()
                             if type(value) in allowed_types)

        self.timems = msecs(kwargs['start'], kwargs['end'])


    @property
    def id(self):
        return "{}-{}-{}-{}".format(self.show.lower(), self.season, formatted_episodes(self.episodes), self.index)


    @property
    def data(self):
        return {"id": self.id, **vars(self)}


    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.id)



class Subtitles:
    def __init__(self, video: 'VideoFile'):
        self.video = video
        self.appsearch = Appsearch()


    @property
    def list(self):
        for subtitle in self.video.extract_subs():
            yield subtitle


    @property
    def documents(self):
        for subtitle in self.list:
            yield Document(**vars(self.video), **vars(subtitle))


    @property
    def documents_chunked(self, chunksize=100):
        iterator = iter(self.documents)
        for first in iterator:
            yield chain([first], islice(iterator, chunksize - 1))


    def index(self):
        for n, chunk in enumerate(self.documents_chunked):
            documents = self.appsearch.index([i.data for i in list(chunk)])
            logger.debug('indexed {} chunk {} containing {}', str(self.video), n, len(documents))
