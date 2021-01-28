# https://github.com/0x64746b/matitor

import re
import sys
from os import path

from sh import Command, ErrorReturnCode

mkvinfo = Command("mkvinfo")
mkvextract = Command("mkvextract")

SUBTITLE_EXTENSION = "srt"


class Track(object):
    def __init__(self, track_number, language, name):
        self._track_number = track_number
        self._language = language
        self._name = name

    @property
    def number(self):
        return self._track_number

    def __str__(self):
        prefix = "Track number {}:".format(self._track_number)

        result = "{} Language: {}\n".format(prefix, self._language)
        if self._name:
            result += "{} Name: {}".format(len(prefix) * " ", self._name)

        return result


class Extractor(object):
    def __init__(self, mkv_file):
        self.mkv_file = mkv_file

    def extract(self, subtitle_file=None):
        tracks = self._get_tracks(self.mkv_file)
        selected_track = tracks[0].number

        self._extract_track(self.mkv_file, selected_track, subtitle_file)

    def _get_tracks(self, mkv_file):
        info = mkvinfo(mkv_file).stdout

        try:
            raw_tracks = self._parse_segment(info)
        except AttributeError:
            raise

        return self._parse_tracks(raw_tracks)

    @staticmethod
    def _parse_segment(info):

        segment = re.search(
            r"^\|\+ Tracks\n" r"^(.*?)" r"^\|\+ ",
            info.decode("utf-8"),
            re.MULTILINE | re.DOTALL,
        ).group(1)

        tracks = segment.split("| + Track\n")

        # return list(filter(lambda x: x != "", tracks))
        return filter(None, tracks)

    @staticmethod
    def _parse_tracks(tracks):

        subtitle_tracks = []

        for track in tracks:
            if re.search("Track type: subtitles", track):
                track_num = re.search(
                    r"Track number: \d+" r" \(track ID for mkvmerge & mkvextract: (\d+)\)\n",
                    track,
                ).group(1)

                language = re.search(r"Language: (.+)", track)

                if language:
                    language = language.group(1)

                name_field = re.search(r"Name: (.+)", track)
                name = name_field.group(1) if name_field else ""

                subtitle_tracks.append(Track(track_num, language, name))

        return subtitle_tracks

    @staticmethod
    def _extract_track(mkv_file, track_number, subtitle_file):
        if subtitle_file is None:
            subtitle_file = "{}.{}".format(path.splitext(mkv_file)[0], SUBTITLE_EXTENSION)

        try:
            for chunk in mkvextract(
                "-q",
                mkv_file,
                "tracks",
                "{}:{}".format(track_number, subtitle_file),
                _iter=True,
                _out_bufsize=64,
            ):
                sys.stdout.write(chunk)
        except ErrorReturnCode as error:
            raise error
