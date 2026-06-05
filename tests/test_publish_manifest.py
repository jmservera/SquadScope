import json
import tempfile
import unittest
from pathlib import Path

import scripts.publish_manifest as publish_manifest


RUN_ID = "123456"
CURRENT_DATETIME = "2026-05-18T08:00:00Z"
WEEK = "2026-W21"


def write_raw(path: Path, *, week: str = WEEK, crawled_at: str = CURRENT_DATETIME) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "week": week,
                "crawled_at": crawled_at,
                "new_repos": [],
                "trending_repos": [],
                "metadata": {"same_day_reuse": "not_reused"},
            }
        ),
        encoding="utf-8",
    )


def write_summary(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\nweek: 2026-W21\n---\n\nbody\n", encoding="utf-8")


class PublishManifestTests(unittest.TestCase):
    def test_ai_candidate_with_fresh_sources_is_eligible(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw)
            write_summary(summary)

            exit_code = publish_manifest.main(
                [
                    "create",
                    "--week",
                    WEEK,
                    "--run-id",
                    RUN_ID,
                    "--current-datetime",
                    CURRENT_DATETIME,
                    "--summary",
                    str(summary),
                    "--published-summary",
                    str(base / "data/analyzed/2026-W21-summary.md"),
                    "--raw-json",
                    str(raw),
                    "--analysis-source",
                    "copilot-cli",
                    "--analysis-model",
                    "copilot-default",
                    "--validation-status",
                    "passed",
                    "--output",
                    str(manifest),
                ]
            )

            self.assertEqual(exit_code, 0)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "publish_eligibility_v1")
            self.assertEqual(payload["analysis"]["ai_status"], "ai")
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "promote")
            self.assertRegex(payload["candidate"]["summary_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(payload["source_artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(publish_manifest.main(["assert-eligible", "--manifest", str(manifest)]), 0)

    def test_no_ai_candidate_is_not_eligible(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw)
            write_summary(summary)

            publish_manifest.main(
                [
                    "create",
                    "--week",
                    WEEK,
                    "--run-id",
                    RUN_ID,
                    "--current-datetime",
                    CURRENT_DATETIME,
                    "--summary",
                    str(summary),
                    "--published-summary",
                    str(base / "data/analyzed/2026-W21-summary.md"),
                    "--raw-json",
                    str(raw),
                    "--analysis-source",
                    "no-ai",
                    "--analysis-model",
                    "none",
                    "--validation-status",
                    "passed",
                    "--output",
                    str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertIn("analysis source is not AI-publishable", payload["promotion"]["reasons"][0])
            with self.assertRaises(SystemExit):
                publish_manifest.main(["assert-eligible", "--manifest", str(manifest)])

    def test_stale_source_artifact_blocks_promotion(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw, crawled_at="2026-05-11T08:00:00Z")
            write_summary(summary)

            publish_manifest.main(
                [
                    "create",
                    "--week",
                    WEEK,
                    "--run-id",
                    RUN_ID,
                    "--current-datetime",
                    CURRENT_DATETIME,
                    "--summary",
                    str(summary),
                    "--published-summary",
                    str(base / "data/analyzed/2026-W21-summary.md"),
                    "--raw-json",
                    str(raw),
                    "--analysis-source",
                    "github-models",
                    "--analysis-model",
                    "openai/gpt-4o",
                    "--validation-status",
                    "passed",
                    "--output",
                    str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["source_artifacts"][0]["freshness"]["status"], "stale")
            self.assertTrue(any("timestamp week mismatch" in reason for reason in payload["promotion"]["reasons"]))


if __name__ == "__main__":
    unittest.main()
