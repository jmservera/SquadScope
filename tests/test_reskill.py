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
            content_root = base / "content"
            wisdom_path = base / ".squad" / "identity" / "wisdom.md"
            skills_dir = base / ".squad" / "skills" / "trend-detection"
            continuity_path = base / ".squad" / "topics" / "ai-ml" / "continuity.md"
            prompt_template = base / "reskill.md"
            output_path = base / ".squad" / "reskill" / "2026-W21.md"
            analyzed_dir.mkdir(parents=True)
            snapshots_dir.mkdir(parents=True)
            wisdom_path.parent.mkdir(parents=True)
            skills_dir.mkdir(parents=True)
            continuity_path.parent.mkdir(parents=True)
            (content_root / "monthly" / "2026").mkdir(parents=True)
            (content_root / "yearly").mkdir(parents=True)
            output_path.parent.mkdir(parents=True)

            for week, score in [("2026-W17", 61), ("2026-W18", 66), ("2026-W19", 70), ("2026-W20", 74), ("2026-W21", 79), ("2026-W22", 84)]:
                (analyzed_dir / f"{week}-summary.md").write_text(
                    f"---\nweek: {week}\nquality_score: {score}\n---\n\n## Trend Analysis\n\n### Signal\n\nSignal {week}.\n",
                    encoding="utf-8",
                )
            (snapshots_dir / "2026-W21-stars.json").write_text(json.dumps({"octo/signal-kit": 120}), encoding="utf-8")
            wisdom_path.write_text("# Wisdom\n\nPrefer durable signals.", encoding="utf-8")
            (skills_dir / "SKILL.md").write_text("# Skill\n\nWatch for wrapper churn.", encoding="utf-8")
            continuity_path.write_text("# Continuity\n\nMonthly theses that held up.", encoding="utf-8")
            (content_root / "monthly" / "2026" / "05.md").write_text("## Month Overview\n\nMonthly context.\n", encoding="utf-8")
            (content_root / "yearly" / "2026.md").write_text("## Narrative\n\nYearly context.\n", encoding="utf-8")
            prompt_template.write_text(
                "out={{OUTPUT_PATH}}\nwisdom={{WISDOM}}\nskills={{SKILLS}}\ncontinuity={{CONTINUITY}}\narchive={{ARCHIVE_CONTEXT}}\nquality={{QUALITY_TREND}}\nanalyses={{RECENT_ANALYSES}}\nsnapshots={{SNAPSHOT_CONTEXT}}\n",
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
                continuity_file=continuity_path,
                content_root=content_root,
                limit=5,
            )

            self.assertIn(f"out={output_path}", prompt)
            self.assertIn("Prefer durable signals.", prompt)
            self.assertIn("Watch for wrapper churn.", prompt)
            self.assertIn("Monthly theses that held up.", prompt)
            self.assertIn("Monthly context.", prompt)
            self.assertIn("Yearly context.", prompt)
            self.assertIn("Average quality score", prompt)
            self.assertNotIn("2026-W17-summary.md", prompt)
            self.assertIn("2026-W18-summary.md", prompt)
            self.assertIn("2026-W21-stars.json", prompt)
            self.assertIn("No snapshot data available for hindsight validation.", prompt)

    def test_render_prompt_resolves_topic_context_defaults(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            prompt_template = base / "reskill.md"
            output_path = base / ".squad" / "reskill" / "2026-W21.md"
            analyzed_dir = base / "data" / "analyzed"
            snapshots_dir = base / "data" / "snapshots"
            content_root = base / "content"
            topic_wisdom = base / ".squad" / "topics" / "ai-ml" / "wisdom.md"
            topic_skills = base / ".squad" / "topics" / "ai-ml" / "skills"
            topic_continuity = base / ".squad" / "topics" / "ai-ml" / "continuity.md"
            analyzed_dir.mkdir(parents=True)
            snapshots_dir.mkdir(parents=True)
            topic_wisdom.parent.mkdir(parents=True)
            topic_skills.mkdir(parents=True)
            prompt_template.write_text("w={{WISDOM}}\ns={{SKILLS}}\nc={{CONTINUITY}}", encoding="utf-8")
            topic_wisdom.write_text("Topic wisdom", encoding="utf-8")
            (topic_skills / "SKILL.md").write_text("Topic skill", encoding="utf-8")
            topic_continuity.write_text("Topic continuity", encoding="utf-8")

            with mock.patch.object(
                reskill,
                "resolve_analysis_context_paths",
                return_value=(topic_wisdom, topic_skills, topic_continuity),
            ) as resolver:
                prompt = reskill.render_prompt(
                    prompt_template_path=prompt_template,
                    current_datetime="2026-05-18T15:22:25.067+02:00",
                    output_path=output_path,
                    analyzed_dir=analyzed_dir,
                    snapshots_dir=snapshots_dir,
                    wisdom_file=reskill.DEFAULT_WISDOM_FILE,
                    skills_dir=reskill.DEFAULT_SKILLS_DIR,
                    continuity_file=reskill.DEFAULT_CONTINUITY_FILE,
                    content_root=content_root,
                    limit=5,
                )

            resolver.assert_called_once_with()
            self.assertIn("Topic wisdom", prompt)
            self.assertIn("Topic skill", prompt)
            self.assertIn("Topic continuity", prompt)

    def test_render_archive_context_caps_monthly_and_yearly_sections(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            content_root = Path(tmpdir) / "content"
            (content_root / "monthly" / "2026").mkdir(parents=True)
            (content_root / "yearly").mkdir(parents=True)
            (content_root / "monthly" / "2026" / "05.md").write_text(
                "## Month Overview\n\n" + " ".join(["monthlytoken"] * 260),
                encoding="utf-8",
            )
            (content_root / "yearly" / "2026.md").write_text(
                "## Narrative\n\n" + " ".join(["yearlytoken"] * 620),
                encoding="utf-8",
            )

            prompt = reskill.render_archive_context("2026-05-18T15:22:25.067+02:00", content_root)

        self.assertLessEqual(prompt.count("monthlytoken"), reskill.ARCHIVE_MONTHLY_MAX_WORDS)
        self.assertLessEqual(prompt.count("yearlytoken"), reskill.ARCHIVE_YEARLY_MAX_WORDS)
        self.assertIn("…", prompt)

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

    def test_main_can_write_prompt_output_sidecar(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            snapshots_dir = base / "data" / "snapshots"
            wisdom_path = base / ".squad" / "identity" / "wisdom.md"
            skills_dir = base / ".squad" / "skills"
            prompt_template = base / "reskill.md"
            output_path = base / ".squad" / "reskill" / "2026-W21.md"
            prompt_output_path = base / "tmp" / "reskill-prompt.txt"
            analyzed_dir.mkdir(parents=True)
            snapshots_dir.mkdir(parents=True)
            wisdom_path.parent.mkdir(parents=True)
            skills_dir.mkdir(parents=True)
            output_path.parent.mkdir(parents=True)
            (analyzed_dir / "2026-W21-summary.md").write_text(
                "---\nweek: 2026-W21\nquality_score: 76\n---\n\nBody\n",
                encoding="utf-8",
            )
            wisdom_path.write_text("# Wisdom\n\nPrefer durable signals.", encoding="utf-8")
            prompt_template.write_text("{{WISDOM}}\n{{QUALITY_TREND}}", encoding="utf-8")

            response = _FakeHTTPResponse(
                json.dumps({"choices": [{"message": {"content": "# Reskill Report\n"}}]}).encode("utf-8")
            )

            with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "token"}, clear=False), mock.patch.object(
                reskill.request, "urlopen", return_value=response
            ):
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
                        "--output",
                        str(output_path),
                        "--prompt-output",
                        str(prompt_output_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(prompt_output_path.exists())
            self.assertIn("Prefer durable signals.", prompt_output_path.read_text(encoding="utf-8"))

    def test_main_handles_model_403_gracefully(self) -> None:
        """When GitHub Models returns 403 (no model access), main exits 0 with a placeholder."""
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            analyzed_dir = base / "data" / "analyzed"
            snapshots_dir = base / "data" / "snapshots"
            wisdom_path = base / ".squad" / "identity" / "wisdom.md"
            skills_dir = base / ".squad" / "skills"
            prompt_template = base / "reskill.md"
            output_path = base / ".squad" / "reskill" / "2026-W21.md"
            analyzed_dir.mkdir(parents=True)
            snapshots_dir.mkdir(parents=True)
            wisdom_path.parent.mkdir(parents=True)
            skills_dir.mkdir(parents=True)
            output_path.parent.mkdir(parents=True)
            wisdom_path.write_text("# Wisdom\n\nPrefer durable signals.", encoding="utf-8")
            prompt_template.write_text("{{WISDOM}}\n{{QUALITY_TREND}}", encoding="utf-8")

            from urllib import error as urlerror
            import io as _io

            fake_body = _io.BytesIO(
                b'{"error":{"code":"no_access","message":"No access to model: openai/gpt-4.1"}}'
            )
            http_err = urlerror.HTTPError(
                url="https://models.github.ai",
                code=403,
                msg="Forbidden",
                hdrs={},  # type: ignore[arg-type]
                fp=fake_body,
            )

            with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "token"}, clear=False), mock.patch.object(
                reskill.request, "urlopen", side_effect=http_err
            ):
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
                        "--output",
                        str(output_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("Reskill skipped", content)
            self.assertIn("403", content)

    def test_github_models_endpoint_rejects_non_allowlisted_host(self) -> None:
        with mock.patch.dict(
            "os.environ",
            {"GITHUB_TOKEN": "token", "GITHUB_MODELS_ENDPOINT": "https://evil.example.com/v1/chat"},
            clear=False,
        ):
            with self.assertRaisesRegex(ValueError, "host must be one of"):
                reskill.call_github_models("prompt")

    def test_github_models_endpoint_accepts_allowlisted_host(self) -> None:
        class _FakeResponse(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *_):
                self.close()
                return False

        response = _FakeResponse(json.dumps({"choices": [{"message": {"content": "# Reskill\n"}}]}).encode("utf-8"))
        with mock.patch.dict(
            "os.environ",
            {"GITHUB_TOKEN": "token", "GITHUB_MODELS_ENDPOINT": reskill.DEFAULT_MODELS_ENDPOINT},
            clear=False,
        ), mock.patch.object(reskill.request, "urlopen", return_value=response):
            markdown = reskill.call_github_models("prompt")
        self.assertEqual(markdown, "# Reskill\n")


if __name__ == "__main__":
    unittest.main()
