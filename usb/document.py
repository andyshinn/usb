from dataclasses import dataclass
from typing import List

import inflect
from dataclasses_json import DataClassJsonMixin

from usb.utils import msecs, formatted_episodes

p = inflect.engine()


@dataclass
class Document(DataClassJsonMixin):
    content: str
    episode: List[int]
    episode_title: str
    index: int
    path: str
    season: int
    seconds_start: float
    seconds_end: float
    title: str

    @property
    def timems(self):
        return msecs(self.seconds_start, self.seconds_end)

    @property
    def id(self):
        return "{}-{}-{}-{}".format(
            self.title.lower(),
            self.season,
            formatted_episodes(self.episode),
            self.index,
        )

    @property
    def seconds_middle(self):
        return (self.seconds_start + self.seconds_end) / 2

    @property
    def data(self):
        return {"id": self.id, **vars(self)}

    @property
    def human_season_episode(self):
        episode_text = p.plural("episode", len(self.episode))
        return f"Season {self.season} {episode_text} {p.join(self.episode)}: {self.episode_title}"
