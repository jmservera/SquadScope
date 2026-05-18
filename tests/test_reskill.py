import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import scripts.reskill as reskill


class _FakeHTTPResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


class ReskillTests(unittest.TestCase):
    def test_render_prompt_includes_recent_context(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            snapshots_dir = base / "data" / "snapshots"
            wisdom_path = base / ".squad" / "identity" / "wisdom.md"
            skills_dir = base / ".squad" / "skills" / "trend-detection"
            prompt_template = base / "reskill.md"
            output_path = base / ".squad" / "reskill" / "2026-W21.md"
            analyzed_dir.mkdir(parents=True)
            snapshots_dir.mkdir(parents=True)
            wisdom_path.parent.mkdir(parents=True)
            skills_dir.mkdir(parents=True)
            output_path.parent.mkdir(parents=True)

            for week, score in [("2026-W17", 61), ("2026-W18", 66), ("2026-W19", 70), ("2026-W20", 74), ("2026-W21", 79), ("2026-W22", 84)]:
                (analyzed_dir / f"{week}-summary.md").write_text(
                    f"---\nweek: {week}\nquality_score: {score}\n---\n\n## Trend Analysis\n\n### Signal\n\nSignal {week}.\n",
                    encoding="utf-8",
                )
            (snapshots_dir / "2026-W21-stars.json").write_text(json.dumps({"octo/signal-kit": 120}), encoding="utf-8")
            wisdom_path.write_text("# Wisdom\n\nPrefer durable signals.", encoding="utf-8")
            (skills_dir / "SKILL.md").write_text("# Skill\n\nWatch for wrapper churn.", encoding="utf-8")
            prompt_template.write_text(
                "out={{OUTPUT_PATH}}\nwisdom={{WISDOM}}\nskills={{SKILLS}}\nquality={{QUALITY_TREND}}\nanalyses={{RECENT_ANALYSES}}\nsnapshots={{SNAPSHOT_CONTEXT}}\n",
                encoding="utf-8",
            )

            prompt = reskill.render_prompt(
                prompt_template_path=prompt_template,
                current_datetime="2026-05-18T15:22:25.067+02:00",
                output_path=output_path,
                analyzed_dir=analyzed_dir,
                snapshots_dir=snapshots_dir,
                wisdom_file=wisdom_path,
                skills_dir=base / ".squad" / "skills",
                limit=5,
            )

            self.assertIn(f"out={output_path}", prompt)
            self.assertIn("Prefer durable signals.", prompt)
            self.assertIn("Watch for wrapper churn.", prompt)
            self.assertIn("Average quality score", prompt)
            self.assertNotIn("2026-W17-summary.md", prompt)
            self.assertIn("2026-W18-summary.md", prompt)
            self.assertIn("2026-W21-stars.json", prompt)
            self.assertIn("No snapshot data available for hindsight validation.", prompt)

    def test_main_writes_default_weekly_report(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            snapshots_dir = base / "data" / "snapshots"
            wisdom_path = base / ".squad" / "identity" / "wisdom.md"
            skills_dir = base / ".squad" / "skills"
            prompt_template = base / "reskill.md"
            analyzed_dir.mkdir(parents=True)
            snapshots_dir.mkdir(parents=True)
            wisdom_path.parent.mkdir(parents=True)
            skills_dir.mkdir(parents=True)
            (analyzed_dir / "2026-W21-summary.md").write_text(
                "---\nweek: 2026-W21\nquality_score: 76\n---\n\nBody\n",
                encoding="utf-8",
            )
            wisdom_path.write_text("# Wisdom\n\nPrefer durable signals.", encoding="utf-8")
            prompt_template.write_text("{{WISDOM}}\n{{QUALITY_TREND}}", encoding="utf-8")

            response = _FakeHTTPResponse(
                json.dumps({"choices": [{"message": {"content": "# Reskill Report\n"}}]}).encode("utf-8")
            )

            with mock.patch.object(reskill, "DEFAULT_REPORT_DIR", base / ".squad" / "reskill"), mock.patch.dict(
                "os.environ", {"GITHUB_TOKEN": "token"}, clear=False
            ), mock.patch.object(reskill.request, "urlopen", return_value=response):
                exit_code = reskill.main(
                    [
                        "--current-datetime",
                        "2026-05-18T15:22:25.067+02:00",
                        "--prompt-template",
                        str(prompt_template),
                        "--analyzed-dir",
                        str(analyzed_dir),
                        "--snapshots-dir",
                        str(snapshots_dir),
                        "--wisdom-file",
                        str(wisdom_path),
                        "--skills-dir",
                        str(skills_dir),
                    ]
                )

            self.assertEqual(exit_code, 0)
            output_path = base / ".squad" / "reskill" / "2026-W21.md"
            self.assertEqual(output_path.read_text(encoding="utf-8"), "# Reskill Report\n")


if __name__ == "__main__":
    unittest.main()
