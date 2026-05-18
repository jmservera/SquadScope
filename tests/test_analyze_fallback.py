import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import scripts.analyze_fallback as analyze_fallback


class _FakeHTTPResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


class AnalyzeFallbackTests(unittest.TestCase):
    def test_find_previous_summary_picks_latest_prior_week(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            analyzed_dir = Path(tmpdir) / "analyzed"
            analyzed_dir.mkdir()
            (analyzed_dir / "2026-W19-summary.md").write_text("old\n", encoding="utf-8")
            (analyzed_dir / "2026-W20-summary.md").write_text("latest\n", encoding="utf-8")
            (analyzed_dir / "2026-W21-summary.md").write_text("current\n", encoding="utf-8")
            (analyzed_dir / "2026-W22-summary.md").write_text("future\n", encoding="utf-8")

            previous = analyze_fallback.find_previous_summary("2026-W21", analyzed_dir)

            self.assertEqual(previous, analyzed_dir / "2026-W20-summary.md")

    def test_find_previous_summary_handles_year_boundaries(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            analyzed_dir = Path(tmpdir) / "analyzed"
            analyzed_dir.mkdir()
            (analyzed_dir / "2026-W01-summary.md").write_text("early\n", encoding="utf-8")
            (analyzed_dir / "2026-W52-summary.md").write_text("latest prior\n", encoding="utf-8")
            (analyzed_dir / "2027-W01-summary.md").write_text("current\n", encoding="utf-8")

            previous = analyze_fallback.find_previous_summary("2027-W01", analyzed_dir)

            self.assertEqual(previous, analyzed_dir / "2026-W52-summary.md")

    def test_render_prompt_replaces_all_placeholders(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw_path = base / "data" / "raw" / "2026-W21.json"
            analyzed_dir = base / "data" / "analyzed"
            prompt_template = base / "prompt.md"
            output_path = analyzed_dir / "2026-W21-summary.md"
            raw_path.parent.mkdir(parents=True)
            analyzed_dir.mkdir(parents=True)

            raw_path.write_text(json.dumps({"week": "2026-W21", "new_repos": [], "trending_repos": []}), encoding="utf-8")
            (analyzed_dir / "2026-W20-summary.md").write_text("previous summary", encoding="utf-8")
            prompt_template.write_text(
                "date={{CURRENT_DATETIME}}\nraw={{RAW_JSON_PATH}}\nout={{OUTPUT_PATH}}\nprev={{PREVIOUS_SUMMARY_PATH_OR_NONE}}\njson={{RAW_JSON_CONTENT}}\nbody={{PREVIOUS_SUMMARY_CONTENT_OR_EMPTY}}\n",
                encoding="utf-8",
            )

            prompt = analyze_fallback.render_prompt(
                prompt_template_path=prompt_template,
                raw_json_path=raw_path,
                output_path=output_path,
                current_datetime="2026-05-18T13:20:07.067+02:00",
                analyzed_dir=analyzed_dir,
            )

            self.assertIn("date=2026-05-18T13:20:07.067+02:00", prompt)
            self.assertIn(f"raw={raw_path}", prompt)
            self.assertIn(f"out={output_path}", prompt)
            self.assertIn("prev=", prompt)
            self.assertIn("previous summary", prompt)
            self.assertIn('"week": "2026-W21"', prompt)
            self.assertNotIn("{{CURRENT_DATETIME}}", prompt)

    def test_extract_markdown_supports_message_parts(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "output_text", "text": "part one"},
                            {"type": "output_text", "output_text": "part two"},
                        ]
                    }
                }
            ]
        }

        markdown = analyze_fallback.extract_markdown(payload)

        self.assertEqual(markdown, "part one\npart two\n")

    def test_main_writes_fallback_output(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw_path = base / "data" / "raw" / "2026-W21.json"
            prompt_template = base / "prompt.md"
            output_path = base / "data" / "analyzed" / "2026-W21-summary.md"
            raw_path.parent.mkdir(parents=True)
            output_path.parent.mkdir(parents=True)
            raw_path.write_text(json.dumps({"week": "2026-W21", "new_repos": [], "trending_repos": []}), encoding="utf-8")
            prompt_template.write_text("{{RAW_JSON_CONTENT}}", encoding="utf-8")

            response = _FakeHTTPResponse(
                json.dumps({"choices": [{"message": {"content": "# Summary\n"}}]}).encode("utf-8")
            )

            with mock.patch.dict("os.environ", {"GITHUB_TOKEN": "token"}, clear=False), mock.patch.object(
                analyze_fallback.request, "urlopen", return_value=response
            ):
                exit_code = analyze_fallback.main(
                    [
                        "--raw-json",
                        str(raw_path),
                        "--output",
                        str(output_path),
                        "--current-datetime",
                        "2026-05-18T13:20:07.067+02:00",
                        "--prompt-template",
                        str(prompt_template),
                        "--analyzed-dir",
                        str(output_path.parent),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(output_path.read_text(encoding="utf-8"), "# Summary\n")


if __name__ == "__main__":
    unittest.main()
