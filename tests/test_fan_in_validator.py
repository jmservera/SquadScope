"""Tests for shared run-context schema and fan-in validation contract.

Covers acceptance criteria from issue #333:
- Shared run-context schema prevents independent wall-clock computation
- Fan-in validation contract: schema/checksum/window consistency,
  deterministic ordering, duplicate handling, stale cache rejection,
  source status metadata, required-vs-optional failure behavior
- Fixture-based byte-stability checks (same inputs → same output)
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from scripts.run_context import (
    SCHEMA_VERSION,
    RunContext,
    build_run_context,
    compute_code_sha,
    contexts_compatible,
    validate_run_context,
)
from scripts.fan_in_validator import (
    DEFAULT_MAX_ARTIFACT_AGE,
    ValidationResult,
    detect_duplicate_repos,
    detect_duplicate_urls,
    run_full_validation,
    validate_artifact_schema,
    validate_checksum_integrity,
    validate_deterministic_ordering,
    validate_stale_artifacts,
    validate_source_status,
    validate_window_consistency,
    verify_byte_stability,
)


# --- Fixtures ---

WEEK = "2026-W24"
SINCE = datetime(2026, 6, 8, 0, 0, 0, tzinfo=UTC)
UNTIL = datetime(2026, 6, 15, 0, 0, 0, tzinfo=UTC)
NOW = datetime(2026, 6, 14, 12, 0, 0, tzinfo=UTC)
SOURCE_CHECKSUM = "a" * 64
TOPIC_CHECKSUM = "b" * 64
CODE_SHA = "c" * 64


def _make_run_context(**overrides: Any) -> RunContext:
    defaults = dict(
        week=WEEK,
        since=SINCE,
        until=UNTIL,
        source_config_checksum=SOURCE_CHECKSUM,
        topic_config_checksum=TOPIC_CHECKSUM,
        code_sha=CODE_SHA,
        created_at=NOW,
    )
    defaults.update(overrides)
    return build_run_context(**defaults)


def _make_rss_artifact(
    source_id: str = "techcrunch",
    articles: list[dict[str, Any]] | None = None,
    run_context: RunContext | None = None,
    crawled_at: str | None = None,
    status_success: bool = True,
) -> dict[str, Any]:
    ctx = run_context or _make_run_context()
    arts = articles or [
        {"url": f"https://example.com/{source_id}/1", "title": "Article 1", "source": source_id},
        {"url": f"https://example.com/{source_id}/2", "title": "Article 2", "source": source_id},
    ]
    artifact = {
        "source_artifact_schema_version": "1",
        "source_id": source_id,
        "crawled_at": crawled_at or NOW.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "run_context": {
            "week": ctx.week,
            "since": ctx.since,
            "until": ctx.until,
            "crawl_window": {"since": ctx.since, "until": ctx.until},
            "source_config_checksum": ctx.source_config_checksum,
            "schema_checksum": "1",
        },
        "status": {"success": status_success, "error_message": "" if status_success else "timeout"},
        "metrics": {
            "total_articles": len(arts),
            "relevant_articles": len(arts),
            "content_checksum": hashlib.sha256(
                json.dumps(arts, sort_keys=True).encode()
            ).hexdigest(),
        },
        "articles": arts,
    }
    # Compute artifact_checksum
    payload = {
        "source_id": artifact["source_id"],
        "run_context": artifact["run_context"],
        "articles": artifact["articles"],
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    artifact["artifact_checksum"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return artifact


# --- Run Context Tests ---


class TestRunContext:
    def test_build_run_context_deterministic_run_id(self):
        ctx1 = _make_run_context()
        ctx2 = _make_run_context()
        assert ctx1.run_id == ctx2.run_id

    def test_build_run_context_different_inputs_different_id(self):
        ctx1 = _make_run_context()
        ctx2 = _make_run_context(source_config_checksum="d" * 64)
        assert ctx1.run_id != ctx2.run_id

    def test_schema_version_is_set(self):
        ctx = _make_run_context()
        assert ctx.schema_version == SCHEMA_VERSION

    def test_run_context_serialization_roundtrip(self):
        ctx = _make_run_context()
        json_str = ctx.to_json()
        restored = RunContext.from_json(json_str)
        assert ctx == restored

    def test_validate_run_context_valid(self):
        ctx = _make_run_context()
        errors = validate_run_context(ctx)
        assert errors == []

    def test_validate_run_context_missing_field(self):
        ctx = _make_run_context()
        data = ctx.to_dict()
        del data["week"]
        errors = validate_run_context(data)
        assert any("week" in e for e in errors)

    def test_validate_run_context_bad_week_format(self):
        ctx = _make_run_context()
        data = ctx.to_dict()
        data["week"] = "2026-24"  # Missing W prefix
        errors = validate_run_context(data)
        assert any("week" in e for e in errors)

    def test_validate_run_context_bad_timestamp(self):
        ctx = _make_run_context()
        data = ctx.to_dict()
        data["since"] = "not-a-timestamp"
        errors = validate_run_context(data)
        assert any("since" in e for e in errors)

    def test_contexts_compatible_identical(self):
        ctx = _make_run_context()
        assert contexts_compatible(ctx, ctx) == []

    def test_contexts_compatible_different_week(self):
        ctx1 = _make_run_context()
        ctx2 = _make_run_context(week="2026-W25")
        mismatches = contexts_compatible(ctx1, ctx2)
        assert any("week" in m for m in mismatches)

    def test_contexts_compatible_different_checksum(self):
        ctx1 = _make_run_context()
        ctx2 = _make_run_context(source_config_checksum="f" * 64)
        mismatches = contexts_compatible(ctx1, ctx2)
        assert len(mismatches) > 0

    def test_prevents_wall_clock_computation(self):
        """Run context enforces that legs cannot compute their own window."""
        ctx = _make_run_context()
        # The since/until are fixed at build time, not computed from wall clock
        assert ctx.since == "2026-06-08T00:00:00Z"
        assert ctx.until == "2026-06-15T00:00:00Z"
        # Even if built at a different time, same inputs yield same window
        ctx2 = build_run_context(
            week=WEEK,
            since=SINCE,
            until=UNTIL,
            source_config_checksum=SOURCE_CHECKSUM,
            topic_config_checksum=TOPIC_CHECKSUM,
            code_sha=CODE_SHA,
            created_at=datetime(2026, 6, 20, 0, 0, 0, tzinfo=UTC),
        )
        assert ctx.since == ctx2.since
        assert ctx.until == ctx2.until


# --- Fan-In Validation Tests ---


class TestFanInValidation:
    def test_validate_artifact_schema_valid(self):
        artifact = _make_rss_artifact()
        errors = validate_artifact_schema(artifact, "1")
        assert errors == []

    def test_validate_artifact_schema_mismatch(self):
        artifact = _make_rss_artifact()
        errors = validate_artifact_schema(artifact, "2")
        assert any("mismatch" in e for e in errors)

    def test_validate_checksum_integrity_valid(self):
        artifact = _make_rss_artifact()
        errors = validate_checksum_integrity(artifact)
        assert errors == []

    def test_validate_checksum_integrity_tampered(self):
        artifact = _make_rss_artifact()
        artifact["artifact_checksum"] = "0" * 64
        errors = validate_checksum_integrity(artifact)
        assert len(errors) > 0

    def test_window_consistency_valid(self):
        ctx = _make_run_context()
        artifacts = [_make_rss_artifact(run_context=ctx)]
        errors = validate_window_consistency(artifacts, ctx)
        assert errors == []

    def test_window_consistency_mismatch(self):
        ctx = _make_run_context()
        artifact = _make_rss_artifact(run_context=ctx)
        artifact["run_context"]["week"] = "2026-W99"
        errors = validate_window_consistency([artifact], ctx)
        assert len(errors) > 0

    def test_deterministic_ordering_sorted(self):
        articles = [
            {"source": "a", "url": "https://a.com/1"},
            {"source": "a", "url": "https://a.com/2"},
            {"source": "b", "url": "https://b.com/1"},
        ]
        errors = validate_deterministic_ordering(articles)
        assert errors == []

    def test_deterministic_ordering_unsorted(self):
        articles = [
            {"source": "b", "url": "https://b.com/1"},
            {"source": "a", "url": "https://a.com/1"},
        ]
        errors = validate_deterministic_ordering(articles)
        assert len(errors) > 0

    def test_detect_duplicate_urls(self):
        articles = [
            {"url": "https://example.com/1"},
            {"url": "https://example.com/1"},
            {"url": "https://example.com/2"},
        ]
        dupes = detect_duplicate_urls(articles)
        assert len(dupes) == 1

    def test_detect_duplicate_urls_normalized(self):
        articles = [
            {"url": "https://example.com/path?query=1"},
            {"url": "https://example.com/path?query=2"},
        ]
        dupes = detect_duplicate_urls(articles)
        # Same path, different query → treated as same after normalization
        assert len(dupes) == 1

    def test_detect_duplicate_repos(self):
        repos = [
            {"full_name": "owner/repo1"},
            {"full_name": "owner/repo1"},
            {"full_name": "owner/repo2"},
        ]
        dupes = detect_duplicate_repos(repos)
        assert dupes == ["owner/repo1"]

    def test_stale_artifact_rejected(self):
        artifact = _make_rss_artifact(
            crawled_at="2026-06-12T00:00:00Z"  # >24h before NOW
        )
        stale = validate_stale_artifacts([artifact], reference_time=NOW)
        assert len(stale) > 0

    def test_fresh_artifact_accepted(self):
        artifact = _make_rss_artifact(
            crawled_at=NOW.strftime("%Y-%m-%dT%H:%M:%SZ")
        )
        stale = validate_stale_artifacts([artifact], reference_time=NOW)
        assert stale == []

    def test_source_status_required_missing(self):
        artifacts = [_make_rss_artifact(source_id="techcrunch")]
        errors, warnings = validate_source_status(
            artifacts, required_sources=["techcrunch", "nvidia_blog"]
        )
        assert any("nvidia_blog" in e for e in errors)

    def test_source_status_required_failed(self):
        artifact = _make_rss_artifact(source_id="techcrunch", status_success=False)
        errors, warnings = validate_source_status(
            [artifact], required_sources=["techcrunch"]
        )
        assert any("techcrunch" in e for e in errors)

    def test_source_status_optional_missing_is_warning(self):
        artifacts = [_make_rss_artifact(source_id="techcrunch")]
        errors, warnings = validate_source_status(
            artifacts,
            required_sources=["techcrunch"],
            optional_sources=["huggingface"],
        )
        assert errors == []
        assert any("huggingface" in w for w in warnings)


# --- Byte Stability Tests ---


class TestByteStability:
    def test_same_inputs_same_output(self):
        """Fixture check: same inputs produce byte-identical output."""
        output1 = {
            "articles": [
                {"url": "https://a.com/1", "source": "a", "title": "A1"},
                {"url": "https://b.com/1", "source": "b", "title": "B1"},
            ],
            "merged_at": "2026-06-14T12:00:00Z",
            "checksum": "abc",
        }
        output2 = {
            "articles": [
                {"url": "https://a.com/1", "source": "a", "title": "A1"},
                {"url": "https://b.com/1", "source": "b", "title": "B1"},
            ],
            "merged_at": "2026-06-14T13:00:00Z",  # Different timestamp
            "checksum": "abc",
        }
        errors = verify_byte_stability(output1, output2)
        assert errors == []  # Timestamps excluded

    def test_different_content_detected(self):
        output1 = {"articles": [{"url": "https://a.com/1"}], "merged_at": "t1"}
        output2 = {"articles": [{"url": "https://b.com/1"}], "merged_at": "t1"}
        errors = verify_byte_stability(output1, output2)
        assert len(errors) > 0

    def test_deterministic_merge_fixture(self):
        """Prove that merging the same artifacts twice yields identical output."""
        ctx = _make_run_context()
        a1 = _make_rss_artifact(source_id="alpha", run_context=ctx)
        a2 = _make_rss_artifact(source_id="beta", run_context=ctx)

        def merge(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
            sorted_arts = sorted(artifacts, key=lambda a: a["source_id"])
            all_articles = []
            for art in sorted_arts:
                all_articles.extend(art.get("articles", []))
            # Deterministic sort
            all_articles.sort(key=lambda a: (a.get("source", ""), a.get("url", "")))
            return {
                "articles": all_articles,
                "sources": [a["source_id"] for a in sorted_arts],
                "checksum": hashlib.sha256(
                    json.dumps(all_articles, sort_keys=True).encode()
                ).hexdigest(),
            }

        result1 = merge([a1, a2])
        result2 = merge([a2, a1])  # Different input order
        errors = verify_byte_stability(result1, result2)
        assert errors == [], "Same artifacts in different order must produce identical output"


# --- Full Validation Integration Tests ---


class TestFullValidation:
    def test_valid_artifacts_pass(self):
        ctx = _make_run_context()
        artifacts = [
            _make_rss_artifact(source_id="techcrunch", run_context=ctx),
            _make_rss_artifact(source_id="nvidia_blog", run_context=ctx),
        ]
        result = run_full_validation(
            artifacts,
            ctx,
            required_sources=["techcrunch", "nvidia_blog"],
            expected_schema_version="1",
            reference_time=NOW,
        )
        assert result.valid
        assert result.errors == []

    def test_empty_artifacts_fail(self):
        ctx = _make_run_context()
        result = run_full_validation([], ctx)
        assert not result.valid
        assert "no artifacts" in result.errors[0]

    def test_schema_mismatch_fails(self):
        ctx = _make_run_context()
        artifact = _make_rss_artifact(run_context=ctx)
        result = run_full_validation(
            [artifact], ctx, expected_schema_version="99"
        )
        assert not result.valid

    def test_missing_required_source_fails(self):
        ctx = _make_run_context()
        artifact = _make_rss_artifact(source_id="techcrunch", run_context=ctx)
        result = run_full_validation(
            [artifact],
            ctx,
            required_sources=["techcrunch", "missing_source"],
            expected_schema_version="1",
            reference_time=NOW,
        )
        assert not result.valid
        assert "missing_source" in str(result.errors)

    def test_optional_missing_source_warns(self):
        ctx = _make_run_context()
        artifact = _make_rss_artifact(source_id="techcrunch", run_context=ctx)
        result = run_full_validation(
            [artifact],
            ctx,
            required_sources=["techcrunch"],
            optional_sources=["huggingface"],
            expected_schema_version="1",
            reference_time=NOW,
        )
        assert result.valid  # Optional missing doesn't fail
        assert "huggingface" in str(result.warnings)
