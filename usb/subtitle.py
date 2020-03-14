import os
import re
import tempfile
from itertools import chain, islice

from srt import Subtitle
from elastic_app_search import Client
from loguru import logger

from usb.utils import formatted_episodes, msecs


API_KEY = os.getenv('APPSEARCH_PRIVATE_KEY')
ENGINE = 'usb'
ENDPOINT = 'appsearch:3002/api/as/v1'


class Document:
    def __init__(self, show, season, episodes, subtitle):
        self.show = show
        self.season = season
        self.episodes = episodes
        self.subindex = subtitle.index
        self.content = subtitle.content
        self.timems = msecs(subtitle.start, subtitle.end)


    @property
    def id(self):
        return "{}-{}-{}-{}".format(self.show.lower(), self.season, formatted_episodes(self.episodes), self.subindex)


    @property
    def data(self):
        return {"id": self.id, **vars(self)}


    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.id)



class Subtitles:
    def __init__(self, video: 'VideoFile'):
        self.video = video
        self.client = Client(base_endpoint=ENDPOINT, api_key=API_KEY ,use_https=False)


    @property
    def list(self):
        for subtitle in self.video.extract_subs():
            yield subtitle


    @property
    def documents(self):
        for subtitle in self.list:
            yield Document(
                self.video.show,
                self.video.season,
                self.video.episodes,
                subtitle
            )


    @property
    def documents_chunked(self, chunksize=100):
        iterator = iter(self.documents)
        for first in iterator:
            yield chain([first], islice(iterator, chunksize - 1))


    def index(self):
        for n, chunk in enumerate(self.documents_chunked):
            documents = self.client.index_documents(ENGINE, [i.data for i in list(chunk)])
            logger.debug('indexed {} chunk {} containing {}', str(self.video), n, len(documents))
