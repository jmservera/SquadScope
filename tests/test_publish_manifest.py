import json
import tempfile
import unittest
from argparse import Namespace
from datetime import datetime
from pathlib import Path

import scripts.crawl as crawl
import scripts.publish_manifest as publish_manifest


RUN_ID = "123456"
CURRENT_DATETIME = "2026-05-18T08:00:00Z"
WEEK = "2026-W21"


def write_raw(
    path: Path,
    *,
    week: str = WEEK,
    crawled_at: str = CURRENT_DATETIME,
    metadata: dict | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "week": week,
                "crawled_at": crawled_at,
                "new_repos": [],
                "trending_repos": [],
                "metadata": metadata or {"same_day_reuse": "not_reused"},
            }
        ),
        encoding="utf-8",
    )


def write_summary(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\nweek: 2026-W21\n---\n\nbody\n", encoding="utf-8")


def write_good_published_summary(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\nweek: 2026-W21\nquality_score: 76\nsummary: good\n---\n\nAI-authored analysis\n",
        encoding="utf-8",
    )


def write_no_ai_summary(path: Path, *, quality_score: int = 70) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nweek: 2026-W21\nquality_score: {quality_score}\nsummary: fallback\n---\n\n"
        "Automated data-only summary generated without AI assistance.\n",
        encoding="utf-8",
    )


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
            self.assertEqual(payload["analysis"]["provenance"]["authorship"], "ai-authored")
            self.assertEqual(payload["analysis"]["provenance"]["provider"], "copilot-cli")
            self.assertEqual(payload["analysis"]["provenance"]["model"], "copilot-default")
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
            self.assertEqual(payload["analysis"]["provenance"]["authorship"], "no-ai-fallback")
            self.assertIn("fallback_reason is required", payload["promotion"]["reasons"][0])
            with self.assertRaises(SystemExit):
                publish_manifest.main(["assert-eligible", "--manifest", str(manifest)])

    def test_no_ai_default_cannot_replace_existing_good_ai_article(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            published = base / "data/analyzed/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw)
            write_no_ai_summary(summary)
            write_good_published_summary(published)

            publish_manifest.main(
                [
                    "create",
                    "--week", WEEK,
                    "--run-id", RUN_ID,
                    "--current-datetime", CURRENT_DATETIME,
                    "--summary", str(summary),
                    "--published-summary", str(published),
                    "--raw-json", str(raw),
                    "--analysis-source", "no-ai",
                    "--analysis-model", "none",
                    "--validation-status", "passed",
                    "--fallback-reason", "copilot quality gate failed",
                    "--attempted-ai-path", "provider=copilot-cli,model=copilot-default,status=failed",
                    "--output", str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertTrue(payload["existing_article"]["good_ai_authored"])
            self.assertIn("no-AI fallback is ineligible to replace", " ".join(payload["promotion"]["reasons"]))

    def test_no_ai_first_publish_requires_explicit_policy_and_quality_gate(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw)
            write_no_ai_summary(summary)

            publish_manifest.main(
                [
                    "create",
                    "--week", WEEK,
                    "--run-id", RUN_ID,
                    "--current-datetime", CURRENT_DATETIME,
                    "--summary", str(summary),
                    "--published-summary", str(base / "data/analyzed/2026-W21-summary.md"),
                    "--raw-json", str(raw),
                    "--analysis-source", "no-ai",
                    "--analysis-model", "none",
                    "--validation-status", "passed",
                    "--fallback-reason", "copilot unavailable",
                    "--attempted-ai-path", "provider=copilot-cli,model=copilot-default,status=failed",
                    "--publish-policy", "allow-no-ai-first-publish",
                    "--actor", "jmservera",
                    "--output", str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["policy"], "allow-no-ai-first-publish")
            self.assertEqual(publish_manifest.main(["assert-eligible", "--manifest", str(manifest)]), 0)

    def test_no_ai_explicit_policy_requires_higher_fallback_quality_score(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw)
            write_no_ai_summary(summary, quality_score=69)

            publish_manifest.main(
                [
                    "create",
                    "--week", WEEK,
                    "--run-id", RUN_ID,
                    "--current-datetime", CURRENT_DATETIME,
                    "--summary", str(summary),
                    "--published-summary", str(base / "data/analyzed/2026-W21-summary.md"),
                    "--raw-json", str(raw),
                    "--analysis-source", "no-ai",
                    "--analysis-model", "none",
                    "--validation-status", "passed",
                    "--fallback-reason", "copilot unavailable",
                    "--attempted-ai-path", "provider=copilot-cli,model=copilot-default,status=failed",
                    "--publish-policy", "allow-no-ai-first-publish",
                    "--output", str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertIn("quality_score must be at least 70", " ".join(payload["promotion"]["reasons"]))

    def test_force_replace_requires_audit_and_allows_no_ai_over_existing_good_article(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            published = base / "data/analyzed/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw)
            write_no_ai_summary(summary)
            write_good_published_summary(published)

            publish_manifest.main(
                [
                    "create",
                    "--week", WEEK,
                    "--run-id", RUN_ID,
                    "--current-datetime", CURRENT_DATETIME,
                    "--summary", str(summary),
                    "--published-summary", str(published),
                    "--raw-json", str(raw),
                    "--analysis-source", "no-ai",
                    "--analysis-model", "none",
                    "--validation-status", "passed",
                    "--fallback-reason", "copilot unavailable",
                    "--attempted-ai-path", "provider=copilot-cli,model=copilot-default,status=failed",
                    "--publish-policy", "force-replace",
                    "--force-reason", "operator approved emergency publish",
                    "--actor", "jmservera",
                    "--output", str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertEqual(payload["audit"]["mode"], "force-replace")
            self.assertEqual(payload["audit"]["actor"], "jmservera")
            self.assertEqual(publish_manifest.main(["assert-eligible", "--manifest", str(manifest)]), 0)

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

    def test_structured_same_day_reuse_metadata_remains_machine_readable(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            reuse_metadata = {
                "same_day_reuse": {
                    "status": "reused",
                    "source": "github",
                    "source_id": "github-search",
                    "original_run_id": "111111",
                    "original_crawled_at": "2026-05-18T06:00:00Z",
                    "reused_at": CURRENT_DATETIME,
                    "week": WEEK,
                    "crawl_window": {"since": "2026-05-11", "until": "2026-05-18"},
                    "crawl_config_checksum": "config-sha",
                    "schema_checksum": "schema-sha",
                    "content_checksum": "content-sha",
                },
                "artifact_checksum": "artifact-sha",
            }
            write_raw(raw, metadata=reuse_metadata)
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
                    "copilot-cli",
                    "--analysis-model",
                    "copilot-default",
                    "--validation-status",
                    "passed",
                    "--output",
                    str(manifest),
                ]
            )

            reuse = json.loads(manifest.read_text(encoding="utf-8"))["source_artifacts"][0]["same_day_reuse"]
            self.assertIsInstance(reuse, dict)
            self.assertEqual(reuse["status"], "reused")
            self.assertEqual(reuse["source"], "github")
            self.assertEqual(reuse["source_id"], "github-search")
            self.assertEqual(reuse["original_run_id"], "111111")
            self.assertEqual(reuse["original_crawled_at"], "2026-05-18T06:00:00Z")
            self.assertEqual(reuse["reused_at"], CURRENT_DATETIME)
            self.assertEqual(reuse["crawl_window"]["since"], "2026-05-11")
            self.assertEqual(reuse["crawl_config_checksum"], "config-sha")
            self.assertEqual(reuse["schema_checksum"], "schema-sha")
            self.assertEqual(reuse["content_checksum"], "content-sha")
            self.assertNotEqual(reuse["status"], str(dict(reuse)))

    def test_manifest_preserves_source_id_from_crawl_reuse_metadata(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            since = datetime(2026, 5, 12, tzinfo=crawl.UTC)
            window_end = datetime(2026, 5, 19, tzinfo=crawl.UTC)
            original_crawled_at = datetime(2026, 5, 19, 8, 0, tzinfo=crawl.UTC)
            reused_at = datetime(2026, 5, 19, 10, 0, tzinfo=crawl.UTC)
            args = Namespace(since="2026-05-12", as_of="2026-05-19", max_results=25, output=str(raw), topic=None, config=None)
            checksum = crawl.github_crawl_config_checksum(args, since, window_end, 25)
            payload = {
                "week": WEEK,
                "crawled_at": crawl.iso_timestamp(original_crawled_at),
                "new_repos": [],
                "trending_repos": [],
                "signals": {"top_topics": []},
                "metadata": {
                    "api_calls_used": 1,
                    "cache_hits": 0,
                    "stale_cache_hits": 0,
                    "rate_limit_limit": None,
                    "rate_limit_remaining": None,
                    "rate_limit_reset": None,
                    "rate_limit_resource": None,
                    "partial_failures": [],
                    "run_id": "111111",
                    "snapshot_path": "data/snapshots/2026-W21-stars.json",
                    "crawl_window": {"since": "2026-05-12", "until": "2026-05-19"},
                    "crawl_config_checksum": checksum,
                    "schema_checksum": crawl.github_schema_checksum(),
                    "same_day_reuse": {"status": "not_reused", "source": "github", "source_id": crawl.GITHUB_SOURCE_ID},
                },
            }
            payload["metadata"]["artifact_checksum"] = crawl.github_artifact_checksum(payload)
            crawl.write_payload(raw, payload)
            reused = crawl.load_reusable_github_payload(
                raw,
                week=WEEK,
                crawled_at=reused_at,
                since=since,
                window_end=window_end,
                config_checksum=checksum,
            )
            self.assertIsNotNone(reused)
            crawl.write_payload(raw, reused)
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
                    "copilot-cli",
                    "--analysis-model",
                    "copilot-default",
                    "--validation-status",
                    "passed",
                    "--output",
                    str(manifest),
                ]
            )

            reuse = json.loads(manifest.read_text(encoding="utf-8"))["source_artifacts"][0]["same_day_reuse"]
            self.assertEqual(reuse["status"], "reused")
            self.assertEqual(reuse["source_id"], "github-search")


if __name__ == "__main__":
    unittest.main()
