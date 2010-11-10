import os
import re
import commands

from errors import CommandError
from errors import UnknownFormat
from errors import UnreadableFile
from errors import InputFileDoesNotExist


class VideoInspector(object):

    _valid = False

    def __init__(self, video_source, ffmpeg_bin="ffmpeg"):
        if not os.path.exists(video_source):
            raise InputFileDoesNotExist()

        self.filename = os.path.basename(video_source)
        self.path = os.path.dirname(video_source)
        self.full_filename = video_source

        self._exec_response = commands.getoutput("%s -i %s 2>&1" % (ffmpeg_bin, self.full_filename))

        if re.search(".*command\snot\sfound", self._exec_response, flags=re.IGNORECASE):
            raise CommandError()

        self._metadata = re.search("(Input \#.*)\n(Must|At\sleast)", self._exec_response, flags=re.MULTILINE | re.DOTALL)

        if re.search("Unknown format", self._exec_response, flags=re.IGNORECASE) or not self._metadata:
            raise UnknownFormat()

        if re.search("Duration: N\/A", self._exec_response, flags=re.IGNORECASE | re.MULTILINE):
            raise UnreadableFile()

        self._metadata = self._metadata.group(1)
        self._valid = True

    def ffmpeg_version(self):
        return self._exec_response.split("\n")[0].split("version")[-1].split(",")[0].strip()

    def ffmpeg_configuration(self):
        return re.search("(\s*configuration:)(.*)\n", self._exec_response).group(2).strip()

    def ffmpeg_libav(self):
        lines = re.search("^(\s*lib.*)+", self._exec_response, flags=re.MULTILINE).group(0).split("\n")
        return [n.strip() for n in lines]

    def ffmpeg_build(self):
        return re.search("(\n\s*)(built on.*)(\n)", self._exec_response).group(2)

    def container(self):
        if not self._valid:
            return
        return re.search("Input \#\d+\,\s*(\S+),\s*from", self._metadata).group(1)

    def raw_duration(self):
        return re.search("Duration:\s*([0-9\:\.]+),", self._exec_response).group(1)

    def duration(self):
        if not self._valid:
            return
        units = self.raw_duration().split(":")
        return (int(units[0]) * 60 * 60 * 1000) + (int(units[1]) * 60 * 1000) + int(float(units[2]) * 1000)

    def _bitrate_match(self):
        return re.search("bitrate: ([0-9\.]+)\s*(.*)\s+", self._metadata)

    def bitrate(self):
        if not self._valid:
            return
        return int(self._bitrate_match().group(1))

    def bitrate_units(self):
        if not self._valid:
            return
        return self._bitrate_match().group(2)

    def fps(self):
        if not self._valid:
            return
        return re.search("([0-9\.]+) (fps|tb)", self._exec_response).group(1)

    def video_stream(self):
        m = re.search("\n\s*Stream.*Video:.*\n", self._exec_response)

        if m:
            return m.group(0).strip()
        return

    def _video_match(self):
        if not self._valid:
            return

        m = re.search("Stream\s*(.*?)[,|:|\(|\[].*?\s*Video:\s*(.*?),\s*(.*?),\s*(\d*)x(\d*)", self.video_stream())

        if not m:
            m = re.search("Stream\s*(.*?)[,|:|\(|\[].*?\s*Video:\s*(.*?),\s*(\d*)x(\d*)", self.video_stream())

        return m

    def video_stream_id(self):
        if not self._valid:
            return
        return self._video_match().group(1)

    def video_codec(self):
        if not self._valid:
            return
        return self._video_match().group(2)

    def video_colorspace(self):
        if not self._valid:
            return
        return self._video_match().group(3)

    def width(self):
        if not self._valid:
            return
        return int(self._video_match().group(4))

    def height(self):
        if not self._valid:
            return
        return int(self._video_match().group(5))

    def resolution(self):
        if not self._valid:
            return
        return "%sx%s" % (self.width(), self.height())

    def audio_stream(self):
        if not self._valid:
            return
        m = re.search("\n\s*Stream.*Audio:.*\n", self._exec_response)
        if m:
            return m.group(0).strip()
        return

    def _audio_match(self):
        if not self._valid:
            return
        return re.search("Stream\s*(.*?)[,|:|\(|\[].*?\s*Audio:\s*(.*?),\s*([0-9\.]*) (\w*),\s*([a-zA-Z:]*)", self.audio_stream())

    def audio_codec(self):
        if not self._valid:
            return
        return self._audio_match().group(2)

    def audio_sample_rate(self):
        if not self._valid:
            return
        return int(self._audio_match().group(3))

    def audio_sample_units(self):
        if not self._valid:
            return
        return self._audio_match().group(4)

    def audio_channels_string(self):
        if not self._valid:
            return
        return self._audio_match().group(5)

    def audio_channels(self):
        if not self._valid:
            return
        cs = self.audio_channels_string()
        if cs == "stereo":
            return 2
        elif cs == "mono":
            return 1
        return

    def audio_stream_id(self):
        if not self._valid:
            return
        return self._audio_match().group(1)
