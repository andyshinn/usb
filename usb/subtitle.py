from itertools import chain, islice
from typing import Iterator

from srt import Subtitle

from usb.document import Document
from usb.logging import logger
from usb.search import Meilisearch
from usb.video import VideoFile


class Subtitles:
    def __init__(self, video: VideoFile):
        self.video = video
        self.search = Meilisearch()

    @property
    def list(self) -> Iterator[Subtitle]:
        yield from self.video.extract_subs()

    @property
    def documents(self):
        for subtitle in self.list:
            yield Document(
                content=subtitle.content,
                episode=self.video.episode,
                episode_title=self.video.episode_title,
                index=subtitle.index,
                path=self.video.path,
                season=self.video.season,
                seconds_start=subtitle.start.total_seconds(),
                seconds_end=subtitle.end.total_seconds(),
                title=self.video.title,
            )

    @property
    def documents_chunked(self, chunksize=100):
        iterator = iter(self.documents)
        for first in iterator:
            yield chain([first], islice(iterator, chunksize - 1))

    def index(self, index_name):
        index = self.search.index(index_name)

        for n, chunk in enumerate(self.documents_chunked):
            documents = index.add_documents([i.data for i in list(chunk)])
            logger.debug("indexed {} chunk {} containing {}", str(self.video), n, len(documents))
