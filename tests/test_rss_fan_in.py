"""Tests for RSS matrix fan-in: per-source artifacts and deterministic merge.

Covers:
- Per-source artifact emission and validation
- Run context building and validation
- Deterministic merge producing canonical output
- Fan-in validation: schema mismatch, window mismatch, missing sources, duplicates
- Partial optional-source failures with warnings
- Deduplication across sources
- Fixture-based determinism proof
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

from scripts.rss_fan_in import (
    SOURCE_ARTIFACT_SCHEMA_VERSION,
    FanInValidationError,
    build_run_context,
    build_source_artifact,
    merge_source_artifacts,
    validate_fan_in_compatibility,
    validate_run_context,
    validate_source_artifact,
)
from scripts.techcrunch_crawler import (
    CANONICAL_SCHEMA_VERSION,
    iso_timestamp,
    schema_checksum,
)

# --- Fixtures ---

NOW = datetime(2026, 6, 13, 12, 0, 0, tzinfo=UTC)
SINCE = datetime(2026, 6, 6, 0, 0, 0, tzinfo=UTC)
UNTIL = datetime(2026, 6, 13, 0, 0, 0, tzinfo=UTC)
WEEK = "2026-W24"
RUN_ID = "test-run-12345"
CONFIG_CHECKSUM = "abc123def456"
SCHEMA_CHECKSUM_VALUE = schema_checksum()


def _make_run_context(**overrides: Any) -> dict[str, Any]:
    ctx = {
        "schema_version": SOURCE_ARTIFACT_SCHEMA_VERSION,
        "run_id": RUN_ID,
        "week": WEEK,
        "crawl_window": {"since": iso_timestamp(SINCE), "until": iso_timestamp(UNTIL)},
        "source_config_checksum": CONFIG_CHECKSUM,
        "schema_checksum": SCHEMA_CHECKSUM_VALUE,
        "sources_requested": ["techcrunch", "github_blog", "nvidia_blog"],
        "required_sources": ["techcrunch", "github_blog"],
        "optional_sources": ["nvidia_blog"],
        "started_at": iso_timestamp(NOW),
        "crawler_code_sha": "sha256-test",
    }
    ctx.update(overrides)
    return ctx


def _make_article(source: str, title: str = "Test Article", url: str = "") -> dict[str, Any]:
    return {
        "source": source,
        "title": title,
        "url": url or f"https://example.com/{source}/{title.lower().replace(' ', '-')}",
        "published_at": iso_timestamp(NOW - timedelta(hours=2)),
        "categories": ["AI", "Open Source"],
        "summary": "A test article about AI and machine learning frameworks.",
        "github_links": ["https://github.com/org/repo"],
        "entities": ["TestCo"],
        "relevance_score": 0.8,
    }


def _make_status(source: str, success: bool = True) -> dict[str, Any]:
    status: dict[str, Any] = {
        "source": source,
        "host": f"{source}.example.com",
        "started_at": iso_timestamp(NOW),
        "ended_at": iso_timestamp(NOW + timedelta(seconds=1)),
        "duration_seconds": 1.0,
        "timeout_seconds": 15,
        "attempts": 1,
        "total_articles": 3 if success else 0,
        "relevant_articles": 2 if success else 0,
        "github_links_found": 1 if success else 0,
        "success": success,
        "error_class": "" if success else "ConnectionError",
        "error_message": "" if success else "Connection refused",
    }
    return status


def _make_source_artifact(
    source_id: str,
    run_context: dict[str, Any] | None = None,
    articles: list[dict[str, Any]] | None = None,
    success: bool = True,
) -> dict[str, Any]:
    ctx = run_context or _make_run_context()
    arts = (
        articles
        if articles is not None
        else [_make_article(source_id, f"Article {i}") for i in range(3)]
    )
    status = _make_status(source_id, success=success)
    return build_source_artifact(
        source_id=source_id,
        articles=arts,
        status=status,
        run_context=ctx,
        crawled_at=NOW,
    )


# --- Run Context Tests ---


class TestRunContext:
    def test_build_run_context(self) -> None:
        ctx = build_run_context(
            run_id=RUN_ID,
            week=WEEK,
            crawl_window={"since": iso_timestamp(SINCE), "until": iso_timestamp(UNTIL)},
            source_config_checksum_value=CONFIG_CHECKSUM,
            schema_checksum_value=SCHEMA_CHECKSUM_VALUE,
            sources_requested=["techcrunch", "github_blog"],
            required_sources=["techcrunch"],
            optional_sources=["github_blog"],
            started_at=iso_timestamp(NOW),
            crawler_code_sha="sha-test",
        )
        assert ctx["run_id"] == RUN_ID
        assert ctx["week"] == WEEK
        assert ctx["sources_requested"] == ["github_blog", "techcrunch"]
        assert ctx["required_sources"] == ["techcrunch"]
        assert ctx["optional_sources"] == ["github_blog"]

    def test_validate_run_context_valid(self) -> None:
        ctx = _make_run_context()
        validate_run_context(ctx)  # Should not raise

    def test_validate_run_context_missing_keys(self) -> None:
        ctx = _make_run_context()
        del ctx["run_id"]
        with pytest.raises(FanInValidationError, match="missing keys"):
            validate_run_context(ctx)

    def test_validate_run_context_bad_schema_version(self) -> None:
        ctx = _make_run_context(schema_version=99)
        with pytest.raises(FanInValidationError, match="schema_version mismatch"):
            validate_run_context(ctx)

    def test_validate_run_context_bad_crawl_window(self) -> None:
        ctx = _make_run_context(crawl_window={"only_since": "x"})
        with pytest.raises(FanInValidationError, match="crawl_window"):
            validate_run_context(ctx)


# --- Per-Source Artifact Tests ---


class TestSourceArtifact:
    def test_build_source_artifact_structure(self) -> None:
        ctx = _make_run_context()
        articles = [_make_article("techcrunch", f"Art {i}") for i in range(3)]
        status = _make_status("techcrunch")

        artifact = build_source_artifact(
            source_id="techcrunch",
            articles=articles,
            status=status,
            run_context=ctx,
            crawled_at=NOW,
        )

        assert artifact["source_artifact_schema_version"] == SOURCE_ARTIFACT_SCHEMA_VERSION
        assert artifact["source_id"] == "techcrunch"
        assert artifact["crawled_at"] == iso_timestamp(NOW)
        assert artifact["run_context"]["run_id"] == RUN_ID
        assert artifact["run_context"]["week"] == WEEK
        assert artifact["status"]["success"] is True
        assert artifact["metrics"]["total_articles"] == 3
        assert artifact["metrics"]["relevant_articles"] == 3
        assert "artifact_checksum" in artifact
        assert len(artifact["artifact_checksum"]) == 64  # SHA-256 hex

    def test_source_artifact_deterministic(self) -> None:
        ctx = _make_run_context()
        articles = [_make_article("techcrunch", f"Art {i}") for i in range(3)]
        status = _make_status("techcrunch")

        a1 = build_source_artifact(
            source_id="techcrunch",
            articles=articles,
            status=status,
            run_context=ctx,
            crawled_at=NOW,
        )
        a2 = build_source_artifact(
            source_id="techcrunch",
            articles=articles,
            status=status,
            run_context=ctx,
            crawled_at=NOW,
        )
        assert a1["artifact_checksum"] == a2["artifact_checksum"]
        assert a1["articles"] == a2["articles"]

    def test_source_artifact_different_order_same_checksum(self) -> None:
        """Articles in different order produce same checksum (sorted internally)."""
        ctx = _make_run_context()
        articles = [_make_article("techcrunch", f"Art {i}") for i in range(3)]
        status = _make_status("techcrunch")

        a1 = build_source_artifact(
            source_id="techcrunch",
            articles=articles,
            status=status,
            run_context=ctx,
            crawled_at=NOW,
        )
        a2 = build_source_artifact(
            source_id="techcrunch",
            articles=list(reversed(articles)),
            status=status,
            run_context=ctx,
            crawled_at=NOW,
        )
        assert a1["artifact_checksum"] == a2["artifact_checksum"]

    def test_validate_source_artifact_valid(self) -> None:
        artifact = _make_source_artifact("techcrunch")
        validate_source_artifact(artifact)  # Should not raise

    def test_validate_source_artifact_bad_schema(self) -> None:
        artifact = _make_source_artifact("techcrunch")
        artifact["source_artifact_schema_version"] = 99
        with pytest.raises(FanInValidationError, match="schema version mismatch"):
            validate_source_artifact(artifact)

    def test_validate_source_artifact_tampered_checksum(self) -> None:
        artifact = _make_source_artifact("techcrunch")
        artifact["artifact_checksum"] = "tampered"
        with pytest.raises(FanInValidationError, match="checksum mismatch"):
            validate_source_artifact(artifact)

    def test_validate_source_artifact_missing_keys(self) -> None:
        artifact = _make_source_artifact("techcrunch")
        del artifact["metrics"]
        with pytest.raises(FanInValidationError, match="missing keys"):
            validate_source_artifact(artifact)


# --- Fan-In Merge Tests ---


class TestMerge:
    def test_merge_basic(self) -> None:
        ctx = _make_run_context()
        artifacts = [
            _make_source_artifact("techcrunch", ctx),
            _make_source_artifact("github_blog", ctx),
        ]

        output, warnings = merge_source_artifacts(artifacts, ctx, merged_at=NOW)

        assert output["schema_version"] == CANONICAL_SCHEMA_VERSION
        assert output["source"] == "external_news"
        assert output["week"] == WEEK
        assert output["crawl_window"] == ctx["crawl_window"]
        assert output["metadata"]["sources_requested"] == [
            "github_blog",
            "nvidia_blog",
            "techcrunch",
        ]
        assert "techcrunch" in output["metadata"]["sources_succeeded"]
        assert "github_blog" in output["metadata"]["sources_succeeded"]
        assert output["metadata"]["fan_in_mode"] == "matrix"
        assert output["metadata"]["total_articles"] >= 0
        assert output["metadata"]["artifact_checksum"]
        # nvidia_blog is optional and missing → warning
        assert any(w.source_id == "nvidia_blog" for w in warnings)

    def test_merge_deterministic(self) -> None:
        """Same inputs always produce same output (excluding crawled_at)."""
        ctx = _make_run_context()
        artifacts = [
            _make_source_artifact("techcrunch", ctx),
            _make_source_artifact("github_blog", ctx),
        ]

        out1, _ = merge_source_artifacts(artifacts, ctx, merged_at=NOW)
        out2, _ = merge_source_artifacts(artifacts, ctx, merged_at=NOW)

        assert out1["metadata"]["artifact_checksum"] == out2["metadata"]["artifact_checksum"]
        assert out1["articles"] == out2["articles"]
        assert (
            out1["metadata"]["source_artifact_provenance"]
            == out2["metadata"]["source_artifact_provenance"]
        )

    def test_merge_different_artifact_order_same_result(self) -> None:
        """Order of input artifacts doesn't affect output."""
        ctx = _make_run_context()
        a1 = _make_source_artifact("techcrunch", ctx)
        a2 = _make_source_artifact("github_blog", ctx)

        out_ab, _ = merge_source_artifacts([a1, a2], ctx, merged_at=NOW)
        out_ba, _ = merge_source_artifacts([a2, a1], ctx, merged_at=NOW)

        assert out_ab["metadata"]["artifact_checksum"] == out_ba["metadata"]["artifact_checksum"]

    def test_merge_deduplicates_across_sources(self) -> None:
        """Articles with same URL from different sources are deduped."""
        ctx = _make_run_context()
        shared_url = "https://example.com/shared-article"
        art_tc = _make_article("techcrunch", "Shared Article", shared_url)
        art_gh = _make_article("github_blog", "Shared Article", shared_url)

        a1 = build_source_artifact(
            source_id="techcrunch",
            articles=[art_tc],
            status=_make_status("techcrunch"),
            run_context=ctx,
            crawled_at=NOW,
        )
        a2 = build_source_artifact(
            source_id="github_blog",
            articles=[art_gh],
            status=_make_status("github_blog"),
            run_context=ctx,
            crawled_at=NOW,
        )

        output, _ = merge_source_artifacts([a1, a2], ctx, merged_at=NOW)
        assert output["metadata"]["dedupe_count"] == 1
        # The merged article preserves both sources
        merged_article = output["articles"][0]
        assert "techcrunch" in merged_article["sources"]
        assert "github_blog" in merged_article["sources"]

    def test_merge_with_failed_optional_source(self) -> None:
        """Optional source failure produces warning but valid output."""
        ctx = _make_run_context(
            required_sources=["techcrunch"],
            optional_sources=["github_blog"],
        )
        a1 = _make_source_artifact("techcrunch", ctx)
        a2 = _make_source_artifact("github_blog", ctx, articles=[], success=False)

        output, warnings = merge_source_artifacts([a1, a2], ctx, merged_at=NOW)

        assert "github_blog" in output["metadata"]["sources_failed"]
        assert any(
            w.category == "source_failure" and w.source_id == "github_blog" for w in warnings
        )
        # Output is still valid
        assert output["metadata"]["artifact_checksum"]


# --- Fan-In Validation Tests ---


class TestValidation:
    def test_rejects_empty_artifacts(self) -> None:
        ctx = _make_run_context()
        with pytest.raises(FanInValidationError, match="No source artifacts"):
            validate_fan_in_compatibility([], ctx)

    def test_rejects_schema_mismatch(self) -> None:
        ctx = _make_run_context()
        artifact = _make_source_artifact("techcrunch", ctx)
        artifact["run_context"]["schema_checksum"] = "wrong"
        # Recompute checksum after tampering
        from scripts.rss_fan_in import _source_artifact_checksum

        artifact["artifact_checksum"] = _source_artifact_checksum(artifact)

        with pytest.raises(FanInValidationError, match="Schema checksum mismatch"):
            validate_fan_in_compatibility([artifact], ctx)

    def test_rejects_window_mismatch(self) -> None:
        ctx = _make_run_context()
        artifact = _make_source_artifact("techcrunch", ctx)
        artifact["run_context"]["crawl_window"] = {"since": "wrong", "until": "wrong"}
        from scripts.rss_fan_in import _source_artifact_checksum

        artifact["artifact_checksum"] = _source_artifact_checksum(artifact)

        with pytest.raises(FanInValidationError, match="Crawl window mismatch"):
            validate_fan_in_compatibility([artifact], ctx)

    def test_rejects_config_checksum_mismatch(self) -> None:
        ctx = _make_run_context()
        artifact = _make_source_artifact("techcrunch", ctx)
        artifact["run_context"]["source_config_checksum"] = "wrong"
        from scripts.rss_fan_in import _source_artifact_checksum

        artifact["artifact_checksum"] = _source_artifact_checksum(artifact)

        with pytest.raises(FanInValidationError, match="Source config checksum mismatch"):
            validate_fan_in_compatibility([artifact], ctx)

    def test_rejects_run_id_mismatch(self) -> None:
        ctx = _make_run_context()
        artifact = _make_source_artifact("techcrunch", ctx)
        artifact["run_context"]["run_id"] = "different-run"
        from scripts.rss_fan_in import _source_artifact_checksum

        artifact["artifact_checksum"] = _source_artifact_checksum(artifact)

        with pytest.raises(FanInValidationError, match="Run ID mismatch"):
            validate_fan_in_compatibility([artifact], ctx)

    def test_rejects_missing_required_sources(self) -> None:
        ctx = _make_run_context(required_sources=["techcrunch", "github_blog"])
        # Only provide techcrunch
        artifact = _make_source_artifact("techcrunch", ctx)

        with pytest.raises(FanInValidationError, match="Missing required source"):
            validate_fan_in_compatibility([artifact], ctx)

    def test_rejects_duplicate_sources(self) -> None:
        ctx = _make_run_context(required_sources=["techcrunch"])
        a1 = _make_source_artifact("techcrunch", ctx)
        a2 = _make_source_artifact("techcrunch", ctx)

        with pytest.raises(FanInValidationError, match="Duplicate source"):
            validate_fan_in_compatibility([a1, a2], ctx)

    def test_warns_missing_optional_source(self) -> None:
        ctx = _make_run_context(
            required_sources=["techcrunch"],
            optional_sources=["nvidia_blog"],
        )
        artifact = _make_source_artifact("techcrunch", ctx)

        warnings = validate_fan_in_compatibility([artifact], ctx)
        assert len(warnings) == 1
        assert warnings[0].source_id == "nvidia_blog"
        assert warnings[0].category == "missing_optional_source"


# --- CLI Integration Tests ---


class TestCLI:
    def test_emit_and_merge_roundtrip(self, tmp_path: Path) -> None:
        """Full roundtrip: emit per-source artifacts then merge them."""
        from scripts.rss_fan_in import main as fan_in_main

        ctx = _make_run_context(
            required_sources=["techcrunch", "github_blog"],
            optional_sources=[],
        )
        ctx_path = tmp_path / "run-context.json"
        ctx_path.write_text(json.dumps(ctx), encoding="utf-8")

        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        # Emit two source artifacts
        for source_id in ["techcrunch", "github_blog"]:
            articles = [_make_article(source_id, f"Art {i}") for i in range(2)]
            articles_path = tmp_path / f"{source_id}-articles.json"
            articles_path.write_text(json.dumps(articles), encoding="utf-8")

            status = _make_status(source_id)
            status_path = tmp_path / f"{source_id}-status.json"
            status_path.write_text(json.dumps(status), encoding="utf-8")

            result = fan_in_main(
                [
                    "emit",
                    "--source",
                    source_id,
                    "--articles",
                    str(articles_path),
                    "--status",
                    str(status_path),
                    "--run-context",
                    str(ctx_path),
                    "--output",
                    str(artifacts_dir / f"{source_id}.json"),
                ]
            )
            assert result == 0

        # Verify artifacts were created
        assert (artifacts_dir / "techcrunch.json").exists()
        assert (artifacts_dir / "github_blog.json").exists()

        # Merge
        merged_path = tmp_path / "merged.json"
        result = fan_in_main(
            [
                "merge",
                "--artifacts-dir",
                str(artifacts_dir),
                "--run-context",
                str(ctx_path),
                "--output",
                str(merged_path),
            ]
        )
        assert result == 0
        assert merged_path.exists()

        # Validate merged output
        merged = json.loads(merged_path.read_text(encoding="utf-8"))
        assert merged["schema_version"] == CANONICAL_SCHEMA_VERSION
        assert merged["source"] == "external_news"
        assert merged["metadata"]["fan_in_mode"] == "matrix"
        assert merged["metadata"]["total_articles"] == 4
        assert "techcrunch" in merged["metadata"]["sources_succeeded"]
        assert "github_blog" in merged["metadata"]["sources_succeeded"]

    def test_validate_command(self, tmp_path: Path) -> None:
        """Validate subcommand checks artifacts without merging."""
        from scripts.rss_fan_in import main as fan_in_main

        ctx = _make_run_context(required_sources=["techcrunch"], optional_sources=[])
        ctx_path = tmp_path / "run-context.json"
        ctx_path.write_text(json.dumps(ctx), encoding="utf-8")

        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        artifact = _make_source_artifact("techcrunch", ctx)
        (artifacts_dir / "techcrunch.json").write_text(json.dumps(artifact), encoding="utf-8")

        result = fan_in_main(
            [
                "validate",
                "--artifacts-dir",
                str(artifacts_dir),
                "--run-context",
                str(ctx_path),
            ]
        )
        assert result == 0

    def test_merge_fails_on_missing_required(self, tmp_path: Path) -> None:
        """Merge fails when required source is missing."""
        from scripts.rss_fan_in import main as fan_in_main

        ctx = _make_run_context(
            required_sources=["techcrunch", "github_blog"],
            optional_sources=[],
        )
        ctx_path = tmp_path / "run-context.json"
        ctx_path.write_text(json.dumps(ctx), encoding="utf-8")

        artifacts_dir = tmp_path / "artifacts"
        artifacts_dir.mkdir()

        # Only provide techcrunch
        artifact = _make_source_artifact("techcrunch", ctx)
        (artifacts_dir / "techcrunch.json").write_text(json.dumps(artifact), encoding="utf-8")

        result = fan_in_main(
            [
                "merge",
                "--artifacts-dir",
                str(artifacts_dir),
                "--run-context",
                str(ctx_path),
                "--output",
                str(tmp_path / "merged.json"),
            ]
        )
        assert result == 1  # Fails due to missing required source


# --- Determinism Proof ---


class TestDeterminism:
    """Fixture-based proof that same inputs → same merged output."""

    def test_deterministic_merge_with_fixed_fixtures(self, tmp_path: Path) -> None:
        """Given fixed input artifacts, merge always produces identical output."""
        ctx = _make_run_context(
            required_sources=["techcrunch", "github_blog", "nvidia_blog"],
            optional_sources=[],
        )

        # Create deterministic articles
        articles_by_source = {}
        for source_id in ["techcrunch", "github_blog", "nvidia_blog"]:
            articles_by_source[source_id] = [
                {
                    "source": source_id,
                    "title": f"{source_id} Article {i}",
                    "url": f"https://{source_id}.example.com/article-{i}",
                    "published_at": "2026-06-12T10:00:00Z",
                    "categories": ["AI"],
                    "summary": f"Summary for {source_id} article {i}",
                    "github_links": [],
                    "entities": [],
                    "relevance_score": 0.8,
                }
                for i in range(3)
            ]

        artifacts = [
            build_source_artifact(
                source_id=sid,
                articles=articles_by_source[sid],
                status=_make_status(sid),
                run_context=ctx,
                crawled_at=NOW,
            )
            for sid in ["techcrunch", "github_blog", "nvidia_blog"]
        ]

        # Merge 10 times and verify all produce identical output
        checksums = set()
        for _ in range(10):
            output, _ = merge_source_artifacts(artifacts, ctx, merged_at=NOW)
            checksums.add(output["metadata"]["artifact_checksum"])

        assert len(checksums) == 1, (
            f"Non-deterministic merge: got {len(checksums)} distinct checksums"
        )
