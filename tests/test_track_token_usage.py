import json
import tempfile
import unittest
from pathlib import Path

import scripts.track_token_usage as track_token_usage


class TrackTokenUsageTests(unittest.TestCase):
    def test_main_estimates_tokens_and_appends_record(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            prompt_path = base / "prompt.txt"
            output_path = base / "output.md"
            usage_file = base / "data" / "metrics" / "token-usage.jsonl"
            prompt_path.write_text("x" * 40, encoding="utf-8")
            output_path.write_text("y" * 20, encoding="utf-8")

            exit_code = track_token_usage.main(
                [
                    "--stage",
                    "analysis",
                    "--source",
                    "copilot-cli",
                    "--model",
                    "claude-sonnet-4",
                    "--current-datetime",
                    "2026-05-19T08:00:00Z",
                    "--week",
                    "2026-W21",
                    "--prompt-file",
                    str(prompt_path),
                    "--output-file",
                    str(output_path),
                    "--usage-file",
                    str(usage_file),
                ]
            )

            self.assertEqual(exit_code, 0)
            records = [json.loads(line) for line in usage_file.read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertEqual(len(records), 1)
            record = records[0]
            self.assertEqual(record["stage"], "analysis")
            self.assertEqual(record["source"], "copilot-cli")
            self.assertEqual(record["model"], "claude-sonnet-4")
            self.assertEqual(record["week"], "2026-W21")
            self.assertEqual(record["input_tokens"], 10)
            self.assertEqual(record["output_tokens"], 5)
            self.assertEqual(record["total_tokens"], 15)
            self.assertEqual(record["cost_usd"], 0.000105)
            self.assertTrue(record["estimated"])

    def test_main_uses_explicit_tokens_when_provided(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            usage_file = base / "token-usage.jsonl"

            exit_code = track_token_usage.main(
                [
                    "--stage",
                    "reskill",
                    "--source",
                    "github-models",
                    "--model",
                    "openai/gpt-4.1",
                    "--current-datetime",
                    "2026-05-19T08:00:00Z",
                    "--input-tokens",
                    "1000",
                    "--output-tokens",
                    "250",
                    "--usage-file",
                    str(usage_file),
                ]
            )

            self.assertEqual(exit_code, 0)
            record = json.loads(usage_file.read_text(encoding="utf-8").strip())
            self.assertEqual(record["input_tokens"], 1000)
            self.assertEqual(record["output_tokens"], 250)
            self.assertEqual(record["total_tokens"], 1250)
            self.assertEqual(record["week"], "2026-W21")
            self.assertEqual(record["cost_usd"], 0.004)
            self.assertFalse(record["estimated"])


class ParseCopilotTranscriptTests(unittest.TestCase):
    def test_parses_input_output_tokens_pattern(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            transcript = Path(tmpdir) / "transcript.md"
            transcript.write_text(
                "# Copilot Session\n\nSome content here.\n\n"
                "---\nInput tokens: 1500\nOutput tokens: 800\n",
                encoding="utf-8",
            )
            result = track_token_usage.parse_copilot_transcript(transcript)
            self.assertEqual(result, (1500, 800))

    def test_parses_prompt_completion_tokens_pattern(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            transcript = Path(tmpdir) / "transcript.md"
            transcript.write_text(
                "```json\n{\"prompt_tokens\": 2000, \"completion_tokens\": 950}\n```\n",
                encoding="utf-8",
            )
            result = track_token_usage.parse_copilot_transcript(transcript)
            self.assertEqual(result, (2000, 950))

    def test_parses_tokens_used_combined_pattern(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            transcript = Path(tmpdir) / "transcript.md"
            transcript.write_text(
                "## Summary\nTokens used: 3000 input, 1200 output\n",
                encoding="utf-8",
            )
            result = track_token_usage.parse_copilot_transcript(transcript)
            self.assertEqual(result, (3000, 1200))

    def test_parses_usage_slash_pattern(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            transcript = Path(tmpdir) / "transcript.md"
            transcript.write_text(
                "Usage: 500/200 tokens (input/output)\n",
                encoding="utf-8",
            )
            result = track_token_usage.parse_copilot_transcript(transcript)
            self.assertEqual(result, (500, 200))

    def test_returns_none_when_no_pattern_found(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            transcript = Path(tmpdir) / "transcript.md"
            transcript.write_text("# Just a normal transcript\nNo usage info here.\n", encoding="utf-8")
            result = track_token_usage.parse_copilot_transcript(transcript)
            self.assertIsNone(result)

    def test_returns_none_for_missing_file(self) -> None:
        result = track_token_usage.parse_copilot_transcript(Path("/nonexistent/path.md"))
        self.assertIsNone(result)


class ParseApiResponseTests(unittest.TestCase):
    def test_parses_openai_compatible_usage(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            response_file = Path(tmpdir) / "response.json"
            response_file.write_text(
                json.dumps({
                    "id": "chatcmpl-abc123",
                    "choices": [{"message": {"content": "Hello"}}],
                    "usage": {"prompt_tokens": 450, "completion_tokens": 120, "total_tokens": 570},
                }),
                encoding="utf-8",
            )
            result = track_token_usage.parse_api_response(response_file)
            self.assertEqual(result, (450, 120))

    def test_returns_none_for_missing_usage(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            response_file = Path(tmpdir) / "response.json"
            response_file.write_text(json.dumps({"choices": []}), encoding="utf-8")
            result = track_token_usage.parse_api_response(response_file)
            self.assertIsNone(result)

    def test_returns_none_for_invalid_json(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            response_file = Path(tmpdir) / "response.json"
            response_file.write_text("not json at all", encoding="utf-8")
            result = track_token_usage.parse_api_response(response_file)
            self.assertIsNone(result)

    def test_returns_none_for_missing_file(self) -> None:
        result = track_token_usage.parse_api_response(Path("/nonexistent/response.json"))
        self.assertIsNone(result)


class TokenSourcePriorityTests(unittest.TestCase):
    """Test the priority ordering: explicit > transcript/api > file-size estimate."""

    def test_transcript_overrides_file_estimate(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            usage_file = base / "token-usage.jsonl"
            prompt_path = base / "prompt.txt"
            output_path = base / "output.md"
            transcript = base / "transcript.md"
            prompt_path.write_text("x" * 400, encoding="utf-8")
            output_path.write_text("y" * 200, encoding="utf-8")
            transcript.write_text("Input tokens: 5000\nOutput tokens: 2500\n", encoding="utf-8")

            exit_code = track_token_usage.main(
                [
                    "--stage", "analysis",
                    "--source", "copilot-cli",
                    "--model", "claude-sonnet-4",
                    "--current-datetime", "2026-05-19T08:00:00Z",
                    "--prompt-file", str(prompt_path),
                    "--output-file", str(output_path),
                    "--transcript", str(transcript),
                    "--usage-file", str(usage_file),
                ]
            )

            self.assertEqual(exit_code, 0)
            record = json.loads(usage_file.read_text(encoding="utf-8").strip())
            self.assertEqual(record["input_tokens"], 5000)
            self.assertEqual(record["output_tokens"], 2500)
            self.assertFalse(record["estimated"])

    def test_api_response_overrides_file_estimate(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            usage_file = base / "token-usage.jsonl"
            prompt_path = base / "prompt.txt"
            api_response = base / "response.json"
            prompt_path.write_text("x" * 400, encoding="utf-8")
            api_response.write_text(
                json.dumps({"usage": {"prompt_tokens": 800, "completion_tokens": 300, "total_tokens": 1100}}),
                encoding="utf-8",
            )

            exit_code = track_token_usage.main(
                [
                    "--stage", "reskill",
                    "--source", "github-models",
                    "--model", "gpt-4.1",
                    "--current-datetime", "2026-05-19T08:00:00Z",
                    "--prompt-file", str(prompt_path),
                    "--api-response", str(api_response),
                    "--usage-file", str(usage_file),
                ]
            )

            self.assertEqual(exit_code, 0)
            record = json.loads(usage_file.read_text(encoding="utf-8").strip())
            self.assertEqual(record["input_tokens"], 800)
            self.assertEqual(record["output_tokens"], 300)
            self.assertFalse(record["estimated"])

    def test_explicit_tokens_override_transcript(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            usage_file = base / "token-usage.jsonl"
            transcript = base / "transcript.md"
            transcript.write_text("Input tokens: 5000\nOutput tokens: 2500\n", encoding="utf-8")

            exit_code = track_token_usage.main(
                [
                    "--stage", "analysis",
                    "--source", "copilot-cli",
                    "--model", "claude-sonnet-4",
                    "--current-datetime", "2026-05-19T08:00:00Z",
                    "--input-tokens", "9999",
                    "--output-tokens", "4444",
                    "--transcript", str(transcript),
                    "--usage-file", str(usage_file),
                ]
            )

            self.assertEqual(exit_code, 0)
            record = json.loads(usage_file.read_text(encoding="utf-8").strip())
            self.assertEqual(record["input_tokens"], 9999)
            self.assertEqual(record["output_tokens"], 4444)
            self.assertFalse(record["estimated"])

    def test_fallback_to_estimate_when_transcript_has_no_usage(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            usage_file = base / "token-usage.jsonl"
            prompt_path = base / "prompt.txt"
            output_path = base / "output.md"
            transcript = base / "transcript.md"
            prompt_path.write_text("x" * 40, encoding="utf-8")
            output_path.write_text("y" * 20, encoding="utf-8")
            transcript.write_text("# No usage info here\n", encoding="utf-8")

            exit_code = track_token_usage.main(
                [
                    "--stage", "analysis",
                    "--source", "copilot-cli",
                    "--model", "claude-sonnet-4",
                    "--current-datetime", "2026-05-19T08:00:00Z",
                    "--prompt-file", str(prompt_path),
                    "--output-file", str(output_path),
                    "--transcript", str(transcript),
                    "--usage-file", str(usage_file),
                ]
            )

            self.assertEqual(exit_code, 0)
            record = json.loads(usage_file.read_text(encoding="utf-8").strip())
            self.assertEqual(record["input_tokens"], 10)
            self.assertEqual(record["output_tokens"], 5)
            self.assertTrue(record["estimated"])


if __name__ == "__main__":
    unittest.main()
