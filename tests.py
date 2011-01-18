import unittest

from video_inspector import VideoInspector


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


if __name__ == "__main__":
    unittest.main()
