import tempfile
import unittest
from pathlib import Path

import scripts.track_quality as track_quality


class TrackQualityTests(unittest.TestCase):
    def test_build_quality_report_summarizes_scores(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            analyzed_dir = Path(tmpdir) / "analyzed"
            analyzed_dir.mkdir()
            (analyzed_dir / "2026-W19-summary.md").write_text(
                "---\nweek: 2026-W19\nquality_score: 65\n---\n\nBody\n",
                encoding="utf-8",
            )
            (analyzed_dir / "2026-W20-summary.md").write_text(
                "---\nweek: 2026-W20\nquality_score: 72\n---\n\nBody\n",
                encoding="utf-8",
            )
            (analyzed_dir / "2026-W21-summary.md").write_text(
                "---\nweek: 2026-W21\nquality_score: 81\n---\n\nBody\n",
                encoding="utf-8",
            )

            report = track_quality.build_quality_report(analyzed_dir)

            self.assertIn("Summaries analyzed: 3", report)
            self.assertIn("Average quality score: 72.7", report)
            self.assertIn("Trend: improving", report)
            self.assertIn("| 2026-W21 | 81 |", report)

    def test_build_quality_report_handles_missing_entries(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            analyzed_dir = Path(tmpdir) / "analyzed"
            analyzed_dir.mkdir()

            report = track_quality.build_quality_report(analyzed_dir)

            self.assertIn("No analyzed summaries", report)
            self.assertIn("_No data available._", report)


if __name__ == "__main__":
    unittest.main()
