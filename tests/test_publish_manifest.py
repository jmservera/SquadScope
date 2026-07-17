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
    path.write_text('---\nweek: "2026-W21"\nquality_score: 75\n---\n\nbody\n', encoding="utf-8")


def write_good_summary(path: Path, *, quality_score: int = 90) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
title: "Good AI Article"
date: {CURRENT_DATETIME}
week: "{WEEK}"
year: 2026
tags: [ai]
categories: [weekly]
repos_featured: 1
stars_tracked: 100
top_repo: "owner/good"
quality_score: {quality_score}
summary: "A good AI-authored weekly summary."
---

## This Week's Trends

Canonical good analysis.
""",
        encoding="utf-8",
    )


def write_no_ai_summary(path: Path, *, quality_score: int = 70) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nweek: 2026-W21\nquality_score: {quality_score}\nsummary: fallback\n---\n\n"
        "Automated data-only summary generated without AI assistance.\n",
        encoding="utf-8",
    )


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


def write_preflight(path: Path, *, degraded: bool = False, publish_eligible: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "prompt_token_budget": 90000,
                "prompt_tokens": 1200,
                "prompt_bytes": 4800,
                "prompt_checksum_sha256": "a" * 64,
                "prompt_within_budget": True,
                "degraded": degraded,
                "publish_eligible": publish_eligible,
                "promotion_policy": (
                    "normal-promotion"
                    if not degraded
                    else "staged/candidate-only by default; degraded compacted output requires an explicit future promotion policy."
                ),
                "degradation_reason": "Prompt was deterministically compacted."
                if degraded
                else None,
                "fallback_policy": "copilot-only",
                "components": [],
                "deterministic_slices": [],
            }
        ),
        encoding="utf-8",
    )


def create_args(
    base: Path,
    raw: Path,
    summary: Path,
    manifest: Path,
    *,
    source: str = "copilot-cli",
    model: str | None = "copilot-default",
    gate_report: Path | None = None,
    validation_status: str = "passed",
    preflight: Path | None | bool = True,
    run_mode: str = "normal",
    source_run_id: str = "",
    raw_store_manifest: Path | None = None,
    synthesis_status: str | None = "available",
    synthesis_file: Path | None = None,
) -> list[str]:
    args = [
        "create",
        "--week",
        WEEK,
        "--run-id",
        RUN_ID,
        "--current-datetime",
        CURRENT_DATETIME,
        "--root",
        str(base),
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
        "--run-mode",
        run_mode,
        "--output",
        str(manifest),
    ]
    if model is not None:
        args.extend(["--analysis-model", model])
    if gate_report is not None:
        args.extend(["--gate-report", str(gate_report)])
    if preflight is True and source == "copilot-cli":
        preflight_path = manifest.parent / "diagnostics" / "analysis-preflight.json"
        write_preflight(preflight_path)
        args.extend(["--preflight-report", str(preflight_path)])
    elif isinstance(preflight, Path):
        args.extend(["--preflight-report", str(preflight)])
    if synthesis_status is not None:
        args.extend(["--synthesis-status", synthesis_status])
        # When we claim synthesis is available we must back it with real provenance
        # (a readable, non-empty file), matching how the workflow signals "available".
        if synthesis_status == "available" and synthesis_file is None:
            synthesis_file = manifest.parent / "diagnostics" / "synthesis-narrative.md"
            synthesis_file.parent.mkdir(parents=True, exist_ok=True)
            synthesis_file.write_text("Weekly synthesis narrative.\n", encoding="utf-8")
    if synthesis_file is not None:
        args.extend(["--synthesis-file", str(synthesis_file)])
    if source_run_id:
        args.extend(["--source-run-id", source_run_id])
    if raw_store_manifest is not None:
        args.extend(["--raw-store-manifest", str(raw_store_manifest)])
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
            self.assertEqual(payload["analysis"]["preflight"]["degraded"], False)
            self.assertEqual(payload["analysis"]["preflight"]["publish_eligible"], True)
            self.assertEqual(
                payload["analysis"]["preflight"]["promotion_policy"], "normal-promotion"
            )
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "promote")
            self.assertRegex(payload["candidate"]["summary_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(payload["source_artifacts"][0]["sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                payload["source_artifacts"][0]["provenance"]["sha256"],
                payload["source_artifacts"][0]["sha256"],
            )
            self.assertEqual(
                payload["source_artifacts"][0]["provenance"]["same_day_reuse"]["status"],
                "not_reused",
            )
            self.assertEqual(assert_eligible_from_root(base, manifest), 0)

    def test_restore_candidate_requires_verified_source_bound_raw_store(self) -> None:
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
            publish_manifest.publish_safety.main(
                [
                    "store-raw",
                    "--root",
                    str(base),
                    "--week",
                    WEEK,
                    "--source-run-id",
                    "26753498571",
                    "--source-artifact-id",
                    "7330965888",
                    "--source-head-sha",
                    "abc123",
                    "--path",
                    "data/raw/2026-W21.json",
                ]
            )
            raw_store_manifest = base / "data/raw-store/2026-W21/26753498571/manifest.json"

            publish_manifest.main(
                create_args(
                    base,
                    raw,
                    summary,
                    manifest,
                    gate_report=gate_report,
                    run_mode="restore",
                    source_run_id="26753498571",
                    raw_store_manifest=raw_store_manifest,
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertTrue(payload["restore"]["verified"])
            self.assertEqual(payload["restore"]["source_run_id"], "26753498571")
            self.assertEqual(payload["restore"]["source_artifact"]["id"], "7330965888")
            self.assertEqual(assert_eligible_from_root(base, manifest), 0)

    def test_restore_candidate_rejects_hash_mismatch_before_acceptance(self) -> None:
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
            publish_manifest.publish_safety.main(
                [
                    "store-raw",
                    "--root",
                    str(base),
                    "--week",
                    WEEK,
                    "--source-run-id",
                    "26753498571",
                    "--source-artifact-id",
                    "7330965888",
                    "--source-head-sha",
                    "abc123",
                    "--path",
                    "data/raw/2026-W21.json",
                ]
            )
            raw_store_manifest = base / "data/raw-store/2026-W21/26753498571/manifest.json"
            raw.write_bytes(b"tampered restored input\n")

            publish_manifest.main(
                create_args(
                    base,
                    raw,
                    summary,
                    manifest,
                    gate_report=gate_report,
                    run_mode="restore",
                    source_run_id="26753498571",
                    raw_store_manifest=raw_store_manifest,
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertFalse(payload["restore"]["verified"])
            self.assertTrue(
                any(
                    "Restored raw input" in reason and "mismatch" in reason
                    for reason in payload["promotion"]["reasons"]
                )
            )
            with self.assertRaises(SystemExit):
                assert_eligible_from_root(base, manifest)

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
                create_args(
                    base,
                    raw,
                    summary,
                    manifest,
                    source="no-ai",
                    model="none",
                    gate_report=gate_report,
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "block")
            self.assertEqual(payload["analysis"]["provenance"]["authorship"], "no-ai-fallback")
            self.assertIn("fallback_reason is required", payload["promotion"]["reasons"][0])
            with self.assertRaises(SystemExit):
                assert_eligible_from_root(base, manifest)

    def test_copilot_ai_candidate_requires_preflight_for_promotion(self) -> None:
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
                create_args(base, raw, summary, manifest, gate_report=gate_report, preflight=False)
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["analysis"]["ai_status"], "ai")
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertTrue(
                any(
                    "preflight report is required" in reason
                    for reason in payload["promotion"]["reasons"]
                )
            )

    def test_github_models_source_is_not_ai_publishable(self) -> None:
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
                create_args(
                    base,
                    raw,
                    summary,
                    manifest,
                    source="github-models",
                    model="openai/gpt-4o",
                    gate_report=gate_report,
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["analysis"]["ai_status"], "unknown")
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertTrue(
                any(
                    "analysis source is not AI-publishable" in reason
                    for reason in payload["promotion"]["reasons"]
                )
            )

    def test_degraded_preflight_candidate_is_staged_only_by_default(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            preflight = base / "data/candidates/2026-W21/123456/diagnostics/analysis-preflight.json"
            write_raw(raw)
            write_summary(summary)
            write_gate_report(gate_report)
            write_preflight(preflight, degraded=True, publish_eligible=False)

            publish_manifest.main(
                create_args(
                    base, raw, summary, manifest, gate_report=gate_report, preflight=preflight
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "block")
            self.assertTrue(payload["analysis"]["preflight"]["degraded"])
            self.assertFalse(payload["analysis"]["preflight"]["publish_eligible"])
            self.assertIn(
                "staged/candidate-only", payload["analysis"]["preflight"]["promotion_policy"]
            )
            self.assertTrue(
                any("publish-ineligible" in reason for reason in payload["promotion"]["reasons"])
            )
            with self.assertRaises(SystemExit):
                assert_eligible_from_root(base, manifest)

    def test_degraded_but_publish_eligible_candidate_is_promotable(self) -> None:
        """Post-compaction within budget: degraded=True + publish_eligible=True is promotable."""
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            preflight = base / "data/candidates/2026-W21/123456/diagnostics/analysis-preflight.json"
            write_raw(raw)
            write_summary(summary)
            write_gate_report(gate_report)
            write_preflight(preflight, degraded=True, publish_eligible=True)

            publish_manifest.main(
                create_args(
                    base, raw, summary, manifest, gate_report=gate_report, preflight=preflight
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "promote")
            self.assertTrue(payload["analysis"]["preflight"]["degraded"])
            self.assertTrue(payload["analysis"]["preflight"]["publish_eligible"])
            # Should not raise — degraded but eligible means promotable
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

            publish_manifest.main(
                create_args(base, raw, summary, manifest, model=None, gate_report=gate_report)
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["analysis"]["model"], "copilot-default")
            self.assertEqual(payload["analysis"]["model_status"], "available")
            self.assertTrue(payload["promotion"]["eligible"])

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
            write_good_summary(published)

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
                    str(published),
                    "--raw-json",
                    str(raw),
                    "--analysis-source",
                    "no-ai",
                    "--analysis-model",
                    "none",
                    "--validation-status",
                    "passed",
                    "--fallback-reason",
                    "copilot quality gate failed",
                    "--attempted-ai-path",
                    "provider=copilot-cli,model=copilot-default,status=failed",
                    "--output",
                    str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "preserve")
            self.assertTrue(payload["existing_article"]["good_ai_authored"])
            self.assertIn(
                "no-AI fallback is ineligible to replace", " ".join(payload["promotion"]["reasons"])
            )

    def test_no_ai_first_publish_requires_explicit_policy_and_quality_gate(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_no_ai_summary(summary)
            write_gate_report(gate_report)

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
                    "--gate-report",
                    str(gate_report),
                    "--fallback-reason",
                    "copilot unavailable",
                    "--attempted-ai-path",
                    "provider=copilot-cli,model=copilot-default,status=failed",
                    "--publish-policy",
                    "allow-no-ai-first-publish",
                    "--actor",
                    "jmservera",
                    "--output",
                    str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["policy"], "allow-no-ai-first-publish")
            self.assertEqual(assert_eligible_from_root(base, manifest), 0)

    def test_no_ai_explicit_policy_requires_higher_fallback_quality_score(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_no_ai_summary(summary, quality_score=69)
            write_gate_report(gate_report)

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
                    "--gate-report",
                    str(gate_report),
                    "--fallback-reason",
                    "copilot unavailable",
                    "--attempted-ai-path",
                    "provider=copilot-cli,model=copilot-default,status=failed",
                    "--publish-policy",
                    "allow-no-ai-first-publish",
                    "--output",
                    str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertIn(
                "quality_score must be at least 70", " ".join(payload["promotion"]["reasons"])
            )

    def test_force_replace_requires_audit_and_allows_no_ai_over_existing_good_article(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            published = base / "data/analyzed/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_no_ai_summary(summary)
            write_good_summary(published)
            write_gate_report(gate_report)

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
                    str(published),
                    "--raw-json",
                    str(raw),
                    "--analysis-source",
                    "no-ai",
                    "--analysis-model",
                    "none",
                    "--validation-status",
                    "passed",
                    "--gate-report",
                    str(gate_report),
                    "--fallback-reason",
                    "copilot unavailable",
                    "--attempted-ai-path",
                    "provider=copilot-cli,model=copilot-default,status=failed",
                    "--publish-policy",
                    "force-replace",
                    "--force-reason",
                    "operator approved emergency publish",
                    "--actor",
                    "jmservera",
                    "--output",
                    str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertEqual(payload["audit"]["mode"], "force-replace")
            self.assertEqual(payload["audit"]["actor"], "jmservera")
            self.assertEqual(assert_eligible_from_root(base, manifest), 0)

    def test_missing_candidate_summary_only_reports_missing_summary(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_gate_report(gate_report)

            publish_manifest.main(
                create_args(base, raw, summary, manifest, gate_report=gate_report)
            )

            reasons = json.loads(manifest.read_text(encoding="utf-8"))["promotion"]["reasons"]
            self.assertTrue(
                any(reason.startswith("candidate summary missing:") for reason in reasons)
            )
            self.assertFalse(any("quality_score" in reason for reason in reasons))

    def test_stale_source_artifact_blocks_promotion_and_preserves_existing_good_summary(
        self,
    ) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            published = base / "data/analyzed/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw, crawled_at="2026-05-11T08:00:00Z")
            write_summary(summary)
            write_good_summary(published)
            write_gate_report(gate_report)

            publish_manifest.main(
                create_args(
                    base,
                    raw,
                    summary,
                    manifest,
                    source="github-models",
                    model="openai/gpt-4o",
                    gate_report=gate_report,
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "preserve")
            self.assertTrue(payload["preservation"]["preserve_existing"])
            self.assertEqual(payload["source_artifacts"][0]["generated_at"], "2026-05-11T08:00:00Z")
            self.assertEqual(payload["source_artifacts"][0]["freshness"]["status"], "stale")
            self.assertTrue(
                any(
                    "timestamp week mismatch" in reason
                    for reason in payload["promotion"]["reasons"]
                )
            )

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

            publish_manifest.main(
                create_args(base, raw, summary, manifest, gate_report=gate_report)
            )

            manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(
                manifest_payload["source_artifacts"][0]["generated_at"], "2026-05-18T08:00:00Z"
            )

    def test_artifact_entry_handles_missing_or_malformed_json(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            missing = base / "data/raw/missing.json"
            malformed = base / "data/raw/malformed.json"
            malformed.parent.mkdir(parents=True, exist_ok=True)
            malformed.write_text("{not json", encoding="utf-8")

            missing_entry = publish_manifest.artifact_entry(
                "raw_github", missing, WEEK, CURRENT_DATETIME
            )
            malformed_entry = publish_manifest.artifact_entry(
                "raw_github", malformed, WEEK, CURRENT_DATETIME
            )

            self.assertEqual(missing_entry["generated_at"], CURRENT_DATETIME)
            self.assertEqual(malformed_entry["generated_at"], CURRENT_DATETIME)
            self.assertEqual(missing_entry["freshness"]["status"], "missing")
            self.assertEqual(malformed_entry["freshness"]["status"], "missing")

    def test_no_ai_candidate_preserves_existing_good_summary(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            published = base / "data/analyzed/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_summary(summary)
            write_good_summary(published)
            write_gate_report(gate_report)

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
                    str(published),
                    "--raw-json",
                    str(raw),
                    "--analysis-source",
                    "no-ai",
                    "--analysis-model",
                    "none",
                    "--validation-status",
                    "passed",
                    "--gate-report",
                    str(gate_report),
                    "--output",
                    str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["promotion"]["decision"], "preserve")
            self.assertTrue(payload["published"]["good"])
            self.assertTrue(payload["preservation"]["preserve_existing"])
            self.assertEqual(
                payload["preservation"]["preserved_summary_path"], published.as_posix()
            )
            self.assertEqual(payload["preservation"]["rejected_candidate_path"], summary.as_posix())

    def test_lower_quality_candidate_preserves_existing_good_summary(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            published = base / "data/analyzed/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
            write_raw(raw)
            write_good_summary(summary, quality_score=70)
            write_good_summary(published, quality_score=90)
            write_gate_report(gate_report)

            publish_manifest.main(
                create_args(base, raw, summary, manifest, gate_report=gate_report)
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["promotion"]["decision"], "preserve")
            self.assertTrue(
                any(
                    "lower than published good quality_score" in reason
                    for reason in payload["promotion"]["reasons"]
                )
            )

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

            reuse = json.loads(manifest.read_text(encoding="utf-8"))["source_artifacts"][0][
                "same_day_reuse"
            ]
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
            args = Namespace(
                since="2026-05-12",
                as_of="2026-05-19",
                max_results=25,
                output=str(raw),
                topic=None,
                config=None,
            )
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
                    "same_day_reuse": {
                        "status": "not_reused",
                        "source": "github",
                        "source_id": crawl.GITHUB_SOURCE_ID,
                    },
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

            reuse = json.loads(manifest.read_text(encoding="utf-8"))["source_artifacts"][0][
                "same_day_reuse"
            ]
            self.assertEqual(reuse["status"], "reused")
            self.assertEqual(reuse["source_id"], "github-search")

    def test_same_week_wrong_day_source_blocks_normal_promotion(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw, crawled_at="2026-05-19T08:00:00Z")
            write_summary(summary)

            publish_manifest.main(
                [
                    "create",
                    "--week",
                    WEEK,
                    "--run-id",
                    RUN_ID,
                    "--current-datetime",
                    "2026-05-20T08:00:00Z",
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

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertTrue(
                any("current UTC run date" in reason for reason in payload["promotion"]["reasons"])
            )

    def test_invalid_current_datetime_fails_manifest_creation(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw = base / "data/raw/2026-W21.json"
            summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
            manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
            write_raw(raw)
            write_summary(summary)

            with self.assertRaises(SystemExit):
                publish_manifest.main(
                    [
                        "create",
                        "--week",
                        WEEK,
                        "--run-id",
                        RUN_ID,
                        "--current-datetime",
                        "not-a-date",
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
            self.assertFalse(manifest.exists())

    def test_candidate_only_mode_blocks_promotion_even_with_valid_sources(self) -> None:
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
                    "copilot-cli",
                    "--analysis-model",
                    "copilot-default",
                    "--validation-status",
                    "passed",
                    "--run-mode",
                    "candidate-only",
                    "--output",
                    str(manifest),
                ]
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["run_mode"], "candidate-only")
            self.assertTrue(
                any("non-publishing" in reason for reason in payload["promotion"]["reasons"])
            )

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
            write_gate_report(
                gate_report, passed=False, errors=["editorial_quality: low-quality summary"]
            )

            publish_manifest.main(
                create_args(base, raw, summary, manifest, gate_report=gate_report)
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertEqual(payload["validation"]["quality_gates"][0]["status"], "failed")
            self.assertTrue(
                any("low-quality summary" in reason for reason in payload["promotion"]["reasons"])
            )

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

            publish_manifest.main(
                create_args(base, raw, summary, manifest, gate_report=gate_report)
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertTrue(
                any(
                    "evidence_citation gate missing" in reason
                    for reason in payload["promotion"]["reasons"]
                )
            )


class FailClosedSynthesisTests(unittest.TestCase):
    """Cover issue #571: required synthesis must fail closed for normal AI publication."""

    def _prepare(self, base: Path) -> tuple[Path, Path, Path, Path]:
        raw = base / "data/raw/2026-W21.json"
        summary = base / "data/candidates/2026-W21/123456/2026-W21-summary.md"
        manifest = base / "data/candidates/2026-W21/123456/publish-manifest.json"
        gate_report = base / "data/candidates/2026-W21/123456/analysis-gate-report.json"
        write_raw(raw)
        write_summary(summary)
        write_gate_report(gate_report)
        return raw, summary, manifest, gate_report

    def _assert_synthesis_blocks(self, status: str) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw, summary, manifest, gate_report = self._prepare(base)

            publish_manifest.main(
                create_args(
                    base,
                    raw,
                    summary,
                    manifest,
                    gate_report=gate_report,
                    synthesis_status=status,
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertTrue(payload["synthesis"]["required"])
            self.assertEqual(payload["synthesis"]["status"], status)
            self.assertFalse(payload["synthesis"]["available"])
            self.assertTrue(
                any(
                    f"required synthesis is {status}" in reason
                    for reason in payload["promotion"]["reasons"]
                ),
                f"expected synthesis reason for status={status!r} in {payload['promotion']['reasons']}",
            )
            with self.assertRaises(SystemExit) as ctx:
                assert_eligible_from_root(base, manifest)
            self.assertIn("synthesis", str(ctx.exception).lower())
            self.assertIn(status, str(ctx.exception))

    def test_missing_synthesis_blocks_normal_ai_publication(self) -> None:
        self._assert_synthesis_blocks("missing")

    def test_empty_synthesis_blocks_normal_ai_publication(self) -> None:
        self._assert_synthesis_blocks("empty")

    def test_failed_synthesis_blocks_normal_ai_publication(self) -> None:
        self._assert_synthesis_blocks("failed")

    def test_available_synthesis_records_provenance_on_manifest(self) -> None:
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw, summary, manifest, gate_report = self._prepare(base)
            synthesis_file = base / "data/diagnostics/2026-W21/synthesis.md"
            synthesis_file.parent.mkdir(parents=True, exist_ok=True)
            synthesis_file.write_text("# Weekly synthesis narrative\n", encoding="utf-8")

            args = create_args(
                base,
                raw,
                summary,
                manifest,
                gate_report=gate_report,
                synthesis_status="available",
                synthesis_file=synthesis_file,
            )
            self.assertEqual(publish_manifest.main(args), 0)

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(payload["promotion"]["eligible"])
            self.assertTrue(payload["synthesis"]["required"])
            self.assertEqual(payload["synthesis"]["status"], "available")
            self.assertTrue(payload["synthesis"]["available"])
            self.assertEqual(
                payload["synthesis"]["path"],
                synthesis_file.as_posix(),
            )
            self.assertRegex(payload["synthesis"]["sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(assert_eligible_from_root(base, manifest), 0)

    def test_dry_run_mode_is_not_gated_by_synthesis(self) -> None:
        """Non-normal/debug modes remain isolated from the fail-closed gate."""
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw, summary, manifest, gate_report = self._prepare(base)

            publish_manifest.main(
                create_args(
                    base,
                    raw,
                    summary,
                    manifest,
                    gate_report=gate_report,
                    synthesis_status="missing",
                    run_mode="dry-run",
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["synthesis"]["required"])
            self.assertFalse(
                any("required synthesis" in reason for reason in payload["promotion"]["reasons"]),
                f"dry-run must not emit synthesis reasons: {payload['promotion']['reasons']}",
            )

    def test_no_ai_normal_mode_is_not_gated_by_synthesis(self) -> None:
        """no-ai fallback publication is governed by its own force-replace path, not synthesis."""
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw, summary, manifest, gate_report = self._prepare(base)

            publish_manifest.main(
                create_args(
                    base,
                    raw,
                    summary,
                    manifest,
                    source="no-ai",
                    model="none",
                    gate_report=gate_report,
                    synthesis_status="missing",
                )
            )

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertFalse(payload["synthesis"]["required"])
            self.assertFalse(
                any("required synthesis" in reason for reason in payload["promotion"]["reasons"]),
                f"no-ai mode must not emit synthesis reasons: {payload['promotion']['reasons']}",
            )

    def test_available_without_file_is_downgraded_and_fails_closed(self) -> None:
        """Claiming 'available' without provenance downgrades to missing and blocks promotion."""
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw, summary, manifest, gate_report = self._prepare(base)

            # Pass status "available" but no synthesis file / provenance.
            args = create_args(
                base,
                raw,
                summary,
                manifest,
                gate_report=gate_report,
                synthesis_status=None,
            )
            args.extend(["--synthesis-status", "available"])
            self.assertEqual(publish_manifest.main(args), 0)

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertTrue(payload["synthesis"]["required"])
            self.assertEqual(payload["synthesis"]["status"], "missing")
            self.assertFalse(payload["synthesis"]["available"])
            self.assertIsNone(payload["synthesis"]["path"])
            self.assertIsNone(payload["synthesis"]["sha256"])
            self.assertFalse(payload["promotion"]["eligible"])
            self.assertTrue(
                any(
                    "no readable, non-empty" in reason for reason in payload["synthesis"]["reasons"]
                ),
                payload["synthesis"]["reasons"],
            )

    def test_available_with_empty_file_is_downgraded(self) -> None:
        """An empty synthesis file cannot back an 'available' claim."""
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw, summary, manifest, gate_report = self._prepare(base)
            empty = base / "diagnostics" / "synthesis-narrative.md"
            empty.parent.mkdir(parents=True, exist_ok=True)
            empty.write_text("", encoding="utf-8")

            args = create_args(
                base,
                raw,
                summary,
                manifest,
                gate_report=gate_report,
                synthesis_status="available",
                synthesis_file=empty,
            )
            self.assertEqual(publish_manifest.main(args), 0)

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(payload["synthesis"]["status"], "missing")
            self.assertIsNone(payload["synthesis"]["path"])
            self.assertFalse(payload["promotion"]["eligible"])

    def test_assert_eligible_requires_synthesis_provenance(self) -> None:
        """assert-eligible rejects a manifest that claims available without path/sha256."""
        tests_root = Path(__file__).resolve().parent
        with tempfile.TemporaryDirectory(dir=tests_root) as tmpdir:
            base = Path(tmpdir)
            raw, summary, manifest, gate_report = self._prepare(base)

            self.assertEqual(
                publish_manifest.main(
                    create_args(base, raw, summary, manifest, gate_report=gate_report)
                ),
                0,
            )
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            # Tamper: strip provenance while leaving status "available".
            payload["synthesis"]["path"] = None
            payload["synthesis"]["sha256"] = None
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(SystemExit) as ctx:
                assert_eligible_from_root(base, manifest)
            self.assertIn("provenance", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
