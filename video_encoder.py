import subprocess
import fcntl
import select
import os
import re

from video_inspector import VideoInspector

from errors import CantOverwrite
from errors import CommandError
from errors import UnknownFormat
from errors import UnreadableFile


class VideoEncoder(object):

    def __init__(self, video_source, ffmpeg_bin="ffmpeg"):
        self._ffmpeg_bin = ffmpeg_bin
        if not isinstance(video_source, VideoInspector):
            self.original_file = VideoInspector(video_source, ffmpeg_bin)
        else:
            self.original_file = video_source

    # %(ffmpeg_bin)s -i %(input_file)s %(output_file)s
    def execute(self, cmd, video_output, callback=None):
        if os.path.exists(video_output) and " -y " not in cmd:
            raise CantOverwrite()

        cmd = cmd % {
            "ffmpeg_bin": self._ffmpeg_bin,
            "input_file": self.original_file.full_filename,
            "output_file": video_output
        }
        cmd = subprocess.Popen(cmd, stderr=subprocess.PIPE)
        if callback:
            fcntl.fcntl(
                cmd.stderr.fileno(),
                fcntl.F_SETFL,
                fcntl.fcntl(
                    cmd.stderr.fileno(),
                    fcntl.F_GETFL
                ) | os.O_NONBLOCK,
            )

            duration = None
            header = ""
            progress_regex = re.compile(
                "frame=.*time=([0-9\:\.]+)",
                flags=re.IGNORECASE
            )
            header_received = False

            while True:
                progressline = select.select([cmd.stderr.fileno()], [], [])[0]
                if progressline:
                    line = cmd.stderr.read()
                    if line == "":
                        break
                    progress_match = progress_regex.match(line)
                    if progress_match:
                        if not header_received:
                            header_received = True

                            if re.search(
                                ".*command\snot\sfound",
                                header,
                                flags=re.IGNORECASE
                            ):
                                raise CommandError()

                            if re.search(
                                "Unknown format",
                                header,
                                flags=re.IGNORECASE
                            ):
                                raise UnknownFormat()

                            if re.search(
                                "Duration: N\/A",
                                header,
                                flags=re.IGNORECASE | re.MULTILINE
                            ):
                                raise UnreadableFile()

                            raw_duration = re.search(
                                "Duration:\s*([0-9\:\.]+),",
                                header
                            )
                            if raw_duration:
                                units = raw_duration.group(1).split(":")
                                duration = (int(units[0]) * 60 * 60 * 1000) + \
                                    (int(units[1]) * 60 * 1000) + \
                                    int(float(units[2]) * 1000)

                        if duration and callback:
                            callback(
                                float(progress_match.group(1)) * 1000,
                                duration
                            )

                    else:
                        header += line
