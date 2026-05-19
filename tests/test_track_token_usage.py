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


if __name__ == "__main__":
    unittest.main()
