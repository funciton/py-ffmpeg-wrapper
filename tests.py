import unittest
import os
import time

from video_inspector import VideoInspector
from video_encoder import VideoEncoder


class TestInspector(unittest.TestCase):

    def setUp(self):
        self._inspector = VideoInspector("input.mp4")

    def testContainer(self):
        self.assertEquals(
            self._inspector.container(),
            "mov,mp4,m4a,3gp,3g2,mj2"
        )

    def testRawDuration(self):
        self.assertEquals(self._inspector.raw_duration(), "00:02:22.70")

    def testDuration(self):
        self.assertEquals(self._inspector.duration(), 142700)

    def testFPS(self):
        self.assertEquals(self._inspector.fps(), '24')


class TestEncoder(unittest.TestCase):

    def setUp(self):
        self._encoder = VideoEncoder("input.mp4")

    def testSyncEncoding(self):
        t = time.time()
        self._encoder.execute(
            "%(ffmpeg_bin)s -i %(input_file)s %(output_file)s",
            "test.avi"
        )
        self.assertTrue(os.path.exists("test.avi"))
        self.assertTrue((time.time() - t) > 5)  # 5 seconds min
        os.remove("test.avi")


if __name__ == "__main__":
    unittest.main()
