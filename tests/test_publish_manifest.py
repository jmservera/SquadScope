import json
import os
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


def write_gate_report(path: Path, *, passed: bool = True, errors: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    gate_errors = errors or []
    gates = {
        "structural_schema": {"passed": passed, "errors": gate_errors if not passed else []},
        "ai_provenance": {"passed": True, "errors": []},
        "evidence_citation": {"passed": True, "errors": []},
        "editorial_quality": {"passed": True, "errors": []},
    }
    path.write_text(
        json.dumps(
            {
                "passed": passed,
                "source": "copilot-cli",
                "model": "copilot-default",
                "failure_class": "passed" if passed else "structural_schema",
                "errors_after_repair": gate_errors,
                "repair_actions": [],
                "gates": gates,
            }
        ),
        encoding="utf-8",
    )


def create_args(base: Path, raw: Path, summary: Path, manifest: Path, *, source: str = "copilot-cli", model: str | None = "copilot-default", gate_report: Path | None = None, validation_status: str = "passed") -> list[str]:
    args = [
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
        source,
        "--validation-status",
        validation_status,
        "--output",
        str(manifest),
    ]
    if model is not None:
        args.extend(["--analysis-model", model])
    if gate_report is not None:
        args.extend(["--gate-report", str(gate_report)])
    return args


def assert_eligible_from_root(root: Path, manifest: Path) -> int:
    previous_cwd = Path.cwd()
    try:
        os.chdir(root)
        return publish_manifest.main(["assert-eligible", "--manifest", str(manifest)])
    finally:
        os.chdir(previous_cwd)


class PublishManifestTests(unittest.TestCase):
    def test_ai_candidate_with_fresh_sources_is_eligible(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_summary(summary)
            write_gate_report(gate_report)

            exit_code = publish_manifest.main(
                create_args(base, raw, summary, manifest, gate_report=gate_report)
            )

            self.assertEqual(exit_code, 0)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], "publish_eligibility_v1")
            self.assertEqual(payload["analysis"]["ai_status"], "ai")
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "promote")
            self.assertRegex(payload["candidate"]["summary_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(payload["source_artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(assert_eligible_from_root(base, manifest), 0)

    def test_no_ai_candidate_is_not_eligible(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_summary(summary)
            write_gate_report(gate_report)

            publish_manifest.main(
                create_args(base, raw, summary, manifest, source="no-ai", model="none", gate_report=gate_report)
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertIn("analysis source is not AI-publishable", payload["promotion"]["reasons"][0])
            with self.assertRaises(SystemExit):
                assert_eligible_from_root(base, manifest)

    def test_copilot_candidate_without_explicit_model_uses_publishable_default(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_summary(summary)
            write_gate_report(gate_report)

            publish_manifest.main(create_args(base, raw, summary, manifest, model=None, gate_report=gate_report))

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["analysis"]["model"], "copilot-default")
            self.assertEqual(payload["analysis"]["model_status"], "available")
            self.assertTrue(payload["promotion"]["eligible"])

    def test_stale_source_artifact_blocks_promotion(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw, crawled_at="2026-05-11T08:00:00Z")
            write_summary(summary)
            write_gate_report(gate_report)

            publish_manifest.main(
                create_args(base, raw, summary, manifest, source="github-models", model="openai/gpt-4o", gate_report=gate_report)
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["source_artifacts"][0]["generated_at"], "2026-05-11T08:00:00Z")
            self.assertEqual(payload["source_artifacts"][0]["freshness"]["status"], "stale")
            self.assertTrue(any("timestamp week mismatch" in reason for reason in payload["promotion"]["reasons"]))

    def test_payload_generated_at_takes_precedence_over_crawled_at(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw, crawled_at="2026-05-18T07:00:00Z")
            payload = json.loads(raw.read_text(encoding="utf-8"))
            payload["generated_at"] = "2026-05-18T08:00:00Z"
            raw.write_text(json.dumps(payload), encoding="utf-8")
            write_summary(summary)
            write_gate_report(gate_report)

            publish_manifest.main(create_args(base, raw, summary, manifest, gate_report=gate_report))

            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(manifest_payload["source_artifacts"][0]["generated_at"], "2026-05-18T08:00:00Z")

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

    def test_failed_gate_report_blocks_promotion(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_summary(summary)
            write_gate_report(gate_report, passed=False, errors=["editorial_quality: low-quality summary"])

            publish_manifest.main(create_args(base, raw, summary, manifest, gate_report=gate_report))

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["validation"]["quality_gates"][0]["status"], "failed")
            self.assertTrue(any("low-quality summary" in reason for reason in payload["promotion"]["reasons"]))

    def test_missing_required_gate_family_blocks_promotion(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_summary(summary)
            write_gate_report(gate_report)
            payload = json.loads(gate_report.read_text(encoding="utf-8"))
            del payload["gates"]["evidence_citation"]
            gate_report.write_text(json.dumps(payload), encoding="utf-8")

            publish_manifest.main(create_args(base, raw, summary, manifest, gate_report=gate_report))

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertTrue(any("evidence_citation gate missing" in reason for reason in payload["promotion"]["reasons"]))


if __name__ == "__main__":
    unittest.main()
