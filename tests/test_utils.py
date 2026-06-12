from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from video_transcriber.models import TranscriptResult, TranscriptSegment
from video_transcriber.utils import format_timestamp, render_transcript_text


class UtilsTestCase(unittest.TestCase):
    def test_format_timestamp_uses_hh_mm_ss(self) -> None:
        self.assertEqual(format_timestamp(0), "00:00:00")
        self.assertEqual(format_timestamp(65), "00:01:05")
        self.assertEqual(format_timestamp(3670), "01:01:10")

    def test_render_transcript_text_with_timestamps(self) -> None:
        result = TranscriptResult(
            source_file=Path("demo.mp4"),
            detected_language="es",
            duration_seconds=10.0,
            segments=[
                TranscriptSegment(start_seconds=0.0, end_seconds=2.0, text=" Hola "),
                TranscriptSegment(start_seconds=2.0, end_seconds=4.0, text="mundo"),
            ],
        )

        rendered = render_transcript_text(result, include_timestamps=True)
        self.assertIn("[00:00:00 -> 00:00:02] Hola", rendered)
        self.assertIn("[00:00:02 -> 00:00:04] mundo", rendered)


if __name__ == "__main__":
    unittest.main()
