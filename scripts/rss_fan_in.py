#!/usr/bin/env python3
"""RSS matrix fan-in: per-source artifact emission and deterministic merge.

This module implements the fan-in mechanism for matrix-based RSS crawling.
Each RSS source emits a per-source artifact with shared run context, and
the merge step combines them deterministically into the canonical
external-news artifact consumed by downstream analysis.

The default in-process RSS crawl path remains unchanged. This fan-in path
activates only when the matrix crawl mode is explicitly enabled.

Usage (emit per-source artifact):
    python -m scripts.rss_fan_in emit \
        --source techcrunch \
        --articles articles.json \
        --output artifacts/techcrunch.json \
        --run-context run-context.json

Usage (merge per-source artifacts):
    python -m scripts.rss_fan_in merge \
        --artifacts-dir artifacts/ \
        --output data/raw/general/2026-W24-external-news.json \
        --run-context run-context.json

References:
    - Issue #436: Implement RSS matrix fan-in
    - Issue #356: Matrix Crawl & Map/Reduce PRD
    - Issue #333: Make canonical artifacts matrix-ready
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.techcrunch_crawler import (
    CANONICAL_SCHEMA_VERSION,
    artifact_checksum,
    dedupe_articles,
    iso_timestamp,
    load_source_configs,
    schema_checksum,
    source_config_checksum,
    source_content_checksum,
    validate_canonical_output,
    week_slug,
)

# Per-source artifact schema version (tracks independently of canonical)
SOURCE_ARTIFACT_SCHEMA_VERSION = 1


class FanInValidationError(Exception):
    """Raised when fan-in validation detects an unrecoverable error."""

    pass


class FanInWarning:
    """Represents a non-fatal fan-in issue that allows merge to proceed."""

    def __init__(self, source_id: str, category: str, message: str) -> None:
        self.source_id = source_id
        self.category = category
        self.message = message

    def to_dict(self) -> dict[str, str]:
        return {
            "source_id": self.source_id,
            "category": self.category,
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# Run Context
# ---------------------------------------------------------------------------


def build_run_context(
    *,
    run_id: str,
    week: str,
    crawl_window: dict[str, str],
    source_config_checksum_value: str,
    schema_checksum_value: str,
    sources_requested: list[str],
    required_sources: list[str] | None = None,
    optional_sources: list[str] | None = None,
    started_at: str | None = None,
    crawler_code_sha: str | None = None,
) -> dict[str, Any]:
    """Build the shared run context distributed to all matrix jobs."""
    all_requested = sorted(sources_requested)
    required = sorted(required_sources or all_requested)
    optional = sorted(optional_sources or [])
    return {
        "schema_version": SOURCE_ARTIFACT_SCHEMA_VERSION,
        "run_id": run_id,
        "week": week,
        "crawl_window": crawl_window,
        "source_config_checksum": source_config_checksum_value,
        "schema_checksum": schema_checksum_value,
        "sources_requested": all_requested,
        "required_sources": required,
        "optional_sources": optional,
        "started_at": started_at or iso_timestamp(datetime.now(UTC)),
        "crawler_code_sha": crawler_code_sha or "",
    }


def validate_run_context(ctx: dict[str, Any]) -> None:
    """Validate run context structure."""
    required_keys = {
        "schema_version",
        "run_id",
        "week",
        "crawl_window",
        "source_config_checksum",
        "schema_checksum",
        "sources_requested",
        "required_sources",
        "started_at",
    }
    missing = sorted(required_keys - set(ctx))
    if missing:
        raise FanInValidationError(f"Run context missing keys: {missing}")
    if ctx["schema_version"] != SOURCE_ARTIFACT_SCHEMA_VERSION:
        raise FanInValidationError(
            f"Run context schema_version mismatch: expected {SOURCE_ARTIFACT_SCHEMA_VERSION}, "
            f"got {ctx['schema_version']}"
        )
    window = ctx.get("crawl_window")
    if not isinstance(window, dict) or "since" not in window or "until" not in window:
        raise FanInValidationError("Run context crawl_window must have 'since' and 'until'")


# ---------------------------------------------------------------------------
# Per-Source Artifact
# ---------------------------------------------------------------------------


def build_source_artifact(
    *,
    source_id: str,
    articles: list[dict[str, Any]],
    status: dict[str, Any],
    run_context: dict[str, Any],
    crawled_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a per-source artifact for one RSS source's crawl results.

    Each per-source artifact contains enough context for the fan-in merge
    to validate provenance, detect staleness, and produce deterministic output.
    """
    validate_run_context(run_context)
    now = crawled_at or datetime.now(UTC)

    # Sort articles deterministically
    sorted_articles = sorted(
        articles,
        key=lambda a: (
            a.get("published_at", ""),
            a.get("url", ""),
            a.get("title", ""),
        ),
        reverse=True,
    )

    content_checksum = source_content_checksum(source_id, sorted_articles)
    relevant_count = sum(1 for a in sorted_articles if a.get("relevance_score", 0) >= 0.4)

    artifact: dict[str, Any] = {
        "source_artifact_schema_version": SOURCE_ARTIFACT_SCHEMA_VERSION,
        "source_id": source_id,
        "crawled_at": iso_timestamp(now),
        "run_context": {
            "run_id": run_context["run_id"],
            "week": run_context["week"],
            "crawl_window": run_context["crawl_window"],
            "source_config_checksum": run_context["source_config_checksum"],
            "schema_checksum": run_context["schema_checksum"],
            "started_at": run_context["started_at"],
            "crawler_code_sha": run_context.get("crawler_code_sha", ""),
        },
        "status": status,
        "metrics": {
            "total_articles": len(sorted_articles),
            "relevant_articles": relevant_count,
            "content_checksum": content_checksum,
        },
        "articles": sorted_articles,
    }

    # Compute artifact-level checksum over deterministic content
    artifact["artifact_checksum"] = _source_artifact_checksum(artifact)
    return artifact


def _source_artifact_checksum(artifact: dict[str, Any]) -> str:
    """Compute a checksum for the per-source artifact content."""
    payload = {
        "source_id": artifact["source_id"],
        "run_context": artifact["run_context"],
        "articles": artifact["articles"],
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def validate_source_artifact(artifact: dict[str, Any]) -> None:
    """Validate a per-source artifact structure."""
    if not isinstance(artifact, dict):
        raise FanInValidationError("Source artifact must be a JSON object")
    if artifact.get("source_artifact_schema_version") != SOURCE_ARTIFACT_SCHEMA_VERSION:
        raise FanInValidationError(
            f"Source artifact schema version mismatch: expected {SOURCE_ARTIFACT_SCHEMA_VERSION}, "
            f"got {artifact.get('source_artifact_schema_version')}"
        )
    required = {"source_id", "crawled_at", "run_context", "status", "metrics", "articles", "artifact_checksum"}
    missing = sorted(required - set(artifact))
    if missing:
        raise FanInValidationError(f"Source artifact missing keys: {missing}")
    # Verify checksum integrity
    expected = _source_artifact_checksum(artifact)
    if artifact["artifact_checksum"] != expected:
        raise FanInValidationError(
            f"Source artifact checksum mismatch for {artifact.get('source_id', '?')}: "
            f"expected {expected}, got {artifact['artifact_checksum']}"
        )


# ---------------------------------------------------------------------------
# Fan-In Merge
# ---------------------------------------------------------------------------


def validate_fan_in_compatibility(
    artifacts: list[dict[str, Any]],
    run_context: dict[str, Any],
) -> list[FanInWarning]:
    """Validate that all per-source artifacts are compatible for merge.

    Returns warnings for non-fatal issues. Raises FanInValidationError for
    unrecoverable problems (schema mismatch, window mismatch, etc.).
    """
    warnings: list[FanInWarning] = []

    if not artifacts:
        raise FanInValidationError("No source artifacts provided for fan-in merge")

    validate_run_context(run_context)

    for artifact in artifacts:
        validate_source_artifact(artifact)
        ctx = artifact["run_context"]
        source_id = artifact["source_id"]

        # Schema version must match
        if ctx.get("schema_checksum") != run_context["schema_checksum"]:
            raise FanInValidationError(
                f"Schema checksum mismatch for source '{source_id}': "
                f"artifact has {ctx.get('schema_checksum')}, "
                f"run context has {run_context['schema_checksum']}"
            )

        # Crawl window must match
        if ctx.get("crawl_window") != run_context["crawl_window"]:
            raise FanInValidationError(
                f"Crawl window mismatch for source '{source_id}': "
                f"artifact has {ctx.get('crawl_window')}, "
                f"run context has {run_context['crawl_window']}"
            )

        # Source config checksum must match
        if ctx.get("source_config_checksum") != run_context["source_config_checksum"]:
            raise FanInValidationError(
                f"Source config checksum mismatch for source '{source_id}': "
                f"artifact has {ctx.get('source_config_checksum')}, "
                f"run context has {run_context['source_config_checksum']}"
            )

        # Run ID must match
        if ctx.get("run_id") != run_context["run_id"]:
            raise FanInValidationError(
                f"Run ID mismatch for source '{source_id}': "
                f"artifact has {ctx.get('run_id')}, "
                f"run context has {run_context['run_id']}"
            )

    # Check for required sources
    provided_sources = {a["source_id"] for a in artifacts}
    required_sources = set(run_context.get("required_sources", []))
    missing_required = sorted(required_sources - provided_sources)
    if missing_required:
        raise FanInValidationError(
            f"Missing required source artifacts: {missing_required}"
        )

    # Check for optional missing sources (warning, not error)
    optional_sources = set(run_context.get("optional_sources", []))
    missing_optional = sorted(optional_sources - provided_sources)
    for source_id in missing_optional:
        warnings.append(FanInWarning(
            source_id=source_id,
            category="missing_optional_source",
            message=f"Optional source '{source_id}' artifact not found",
        ))

    # Duplicate source check
    source_ids = [a["source_id"] for a in artifacts]
    seen: set[str] = set()
    for sid in source_ids:
        if sid in seen:
            raise FanInValidationError(f"Duplicate source artifact for '{sid}'")
        seen.add(sid)

    return warnings


def merge_source_artifacts(
    artifacts: list[dict[str, Any]],
    run_context: dict[str, Any],
    *,
    merged_at: datetime | None = None,
) -> tuple[dict[str, Any], list[FanInWarning]]:
    """Deterministically merge per-source artifacts into the canonical output.

    The merge is deterministic: given the same set of per-source artifacts
    and run context, it always produces the same canonical output (minus
    the crawled_at timestamp which is excluded from the checksum).

    Returns (canonical_output, warnings).
    """
    warnings = validate_fan_in_compatibility(artifacts, run_context)
    now = merged_at or datetime.now(UTC)

    # Sort artifacts by source_id for deterministic processing
    sorted_artifacts = sorted(artifacts, key=lambda a: a["source_id"])

    # Collect all articles from all sources
    all_articles: list[dict[str, Any]] = []
    source_statuses: list[dict[str, Any]] = []
    source_provenance: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    for artifact in sorted_artifacts:
        source_id = artifact["source_id"]
        status = artifact.get("status", {})

        all_articles.extend(artifact.get("articles", []))
        source_statuses.append(status)

        if not status.get("success", False):
            warnings.append(FanInWarning(
                source_id=source_id,
                category="source_failure",
                message=f"Source '{source_id}' reported failure: {status.get('error_message', 'unknown')}",
            ))
            if status.get("error_class") or status.get("error_message"):
                errors.append({
                    "source": source_id,
                    "error_class": status.get("error_class", "Unknown"),
                    "error": status.get("error_message", "unknown error"),
                })

        provenance_entry = {
            "source_id": source_id,
            "action": "matrix_fan_in",
            "artifact_checksum": artifact["artifact_checksum"],
            "content_checksum": artifact["metrics"]["content_checksum"],
            "original_run_id": run_context["run_id"],
            "original_crawled_at": artifact["crawled_at"],
            "evaluated_at": iso_timestamp(now),
            "date": now.astimezone(UTC).date().isoformat(),
            "week": run_context["week"],
            "crawl_window": run_context["crawl_window"],
            "source_config_checksum": run_context["source_config_checksum"],
            "schema_checksum": run_context["schema_checksum"],
            "reasons": [],
        }
        source_provenance.append(provenance_entry)

    # Build reuse summary entries for fan-in sources
    reuse_summary = [
        {
            "source": artifact["source_id"],
            "action": "matrix_fan_in",
            "reused": False,
            "refreshed": True,
            "reasons": [],
        }
        for artifact in sorted_artifacts
    ]

    # Build canonical output using the shared build_output function
    requested_sources = sorted(run_context.get("sources_requested", []))
    succeeded = sorted(a["source_id"] for a in sorted_artifacts if a["status"].get("success"))
    failed = sorted(a["source_id"] for a in sorted_artifacts if not a["status"].get("success"))

    output = build_canonical_merged_output(
        articles=all_articles,
        crawled_at=now,
        run_context=run_context,
        source_statuses=source_statuses,
        source_provenance=source_provenance,
        reuse_summary=reuse_summary,
        errors=errors,
        requested_sources=requested_sources,
        succeeded_sources=succeeded,
        failed_sources=failed,
    )

    return output, warnings


def build_canonical_merged_output(
    *,
    articles: list[dict[str, Any]],
    crawled_at: datetime,
    run_context: dict[str, Any],
    source_statuses: list[dict[str, Any]],
    source_provenance: list[dict[str, Any]],
    reuse_summary: list[dict[str, Any]],
    errors: list[dict[str, str]],
    requested_sources: list[str],
    succeeded_sources: list[str],
    failed_sources: list[str],
) -> dict[str, Any]:
    """Build the canonical merged external-news artifact from fan-in results.

    This uses the same schema as the non-matrix path to ensure downstream
    compatibility.
    """
    # Deduplicate articles (same logic as non-matrix path)
    deduped_articles, dedupe_count = dedupe_articles(articles)
    relevant = [a for a in deduped_articles if a.get("relevance_score", 0) >= 0.4]

    all_github_links: set[str] = set()
    for a in deduped_articles:
        all_github_links.update(a.get("github_links", []))

    output: dict[str, Any] = {
        "schema_version": CANONICAL_SCHEMA_VERSION,
        "week": run_context["week"],
        "source": "external_news",
        "crawled_at": iso_timestamp(crawled_at),
        "crawl_window": run_context["crawl_window"],
        "articles": deduped_articles,
        "metadata": {
            "run_id": run_context["run_id"],
            "source_count": len(requested_sources),
            "source_config_checksum": run_context["source_config_checksum"],
            "schema_checksum": run_context["schema_checksum"],
            "sources_requested": sorted(requested_sources),
            "sources_succeeded": sorted(succeeded_sources),
            "sources_failed": sorted(failed_sources),
            "source_status": sorted(source_statuses, key=lambda s: s.get("source", "")),
            "source_reuse_summary": sorted(reuse_summary, key=lambda s: s.get("source", "")),
            "source_artifact_provenance": sorted(source_provenance, key=lambda s: s.get("source_id", "")),
            "sources_with_articles": dict(sorted(
                {str(a.get("source", "unknown")): 0 for a in deduped_articles}.items()
            )),
            "total_articles": len(deduped_articles),
            "relevant_articles": len(relevant),
            "github_links_found": len(all_github_links),
            "dedupe_count": dedupe_count,
            "errors": sorted(errors, key=lambda e: e.get("source", "")),
            "fan_in_mode": "matrix",
            "crawler_code_sha": run_context.get("crawler_code_sha", ""),
        },
    }

    # Compute per-source article counts
    from collections import Counter

    by_source = Counter(str(a.get("source", "unknown")) for a in deduped_articles)
    output["metadata"]["sources_with_articles"] = dict(sorted(by_source.items()))

    # Compute and set artifact checksum
    output["metadata"]["artifact_checksum"] = artifact_checksum(output)

    # Fill in provenance checksums that reference the merged artifact
    for entry in output["metadata"]["source_artifact_provenance"]:
        if not entry.get("artifact_checksum"):
            entry["artifact_checksum"] = output["metadata"]["artifact_checksum"]

    validate_canonical_output(output)
    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def cmd_emit(args: argparse.Namespace) -> int:
    """Emit a per-source artifact from crawl results."""
    run_context = json.loads(Path(args.run_context).read_text(encoding="utf-8"))
    validate_run_context(run_context)

    articles = json.loads(Path(args.articles).read_text(encoding="utf-8"))
    if not isinstance(articles, list):
        print("ERROR: articles file must contain a JSON array", file=sys.stderr)
        return 1

    status = json.loads(Path(args.status).read_text(encoding="utf-8")) if args.status else {
        "source": args.source,
        "success": True,
    }

    artifact = build_source_artifact(
        source_id=args.source,
        articles=articles,
        status=status,
        run_context=run_context,
    )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2, ensure_ascii=False)

    print(f"Emitted per-source artifact for '{args.source}' → {out_path}", file=sys.stderr)
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    """Merge per-source artifacts into canonical output."""
    run_context = json.loads(Path(args.run_context).read_text(encoding="utf-8"))
    validate_run_context(run_context)

    artifacts_dir = Path(args.artifacts_dir)
    if not artifacts_dir.is_dir():
        print(f"ERROR: artifacts directory not found: {artifacts_dir}", file=sys.stderr)
        return 1

    # Load all per-source artifact files
    artifact_files = sorted(artifacts_dir.glob("*.json"))
    if not artifact_files:
        print(f"ERROR: no .json artifacts found in {artifacts_dir}", file=sys.stderr)
        return 1

    artifacts: list[dict[str, Any]] = []
    for path in artifact_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"ERROR: failed to read artifact {path}: {exc}", file=sys.stderr)
            return 1
        # Skip non-source-artifact files (e.g., run-context.json in same dir)
        if not isinstance(data, dict) or "source_artifact_schema_version" not in data:
            continue
        artifacts.append(data)

    if not artifacts:
        print(f"ERROR: no valid source artifacts found in {artifacts_dir}", file=sys.stderr)
        return 1

    try:
        output, warnings = merge_source_artifacts(artifacts, run_context)
    except FanInValidationError as exc:
        print(f"ERROR: fan-in validation failed: {exc}", file=sys.stderr)
        return 1

    for w in warnings:
        print(f"WARNING [{w.category}] {w.source_id}: {w.message}", file=sys.stderr)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    total = output["metadata"]["total_articles"]
    relevant = output["metadata"]["relevant_articles"]
    dedupe = output["metadata"]["dedupe_count"]
    sources = len(artifacts)
    print(
        f"Merged {total} articles from {sources} sources "
        f"({relevant} relevant, {dedupe} deduped) → {out_path}",
        file=sys.stderr,
    )
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate per-source artifacts against run context without merging."""
    run_context = json.loads(Path(args.run_context).read_text(encoding="utf-8"))
    validate_run_context(run_context)

    artifacts_dir = Path(args.artifacts_dir)
    artifact_files = sorted(artifacts_dir.glob("*.json"))
    artifacts: list[dict[str, Any]] = []
    for path in artifact_files:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"ERROR: failed to read {path}: {exc}", file=sys.stderr)
            return 1
        if isinstance(data, dict) and "source_artifact_schema_version" in data:
            artifacts.append(data)

    if not artifacts:
        print(f"ERROR: no valid source artifacts in {artifacts_dir}", file=sys.stderr)
        return 1

    try:
        warnings = validate_fan_in_compatibility(artifacts, run_context)
    except FanInValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    for w in warnings:
        print(f"WARNING [{w.category}] {w.source_id}: {w.message}", file=sys.stderr)

    print(f"OK: {len(artifacts)} source artifacts validated successfully", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="RSS matrix fan-in: per-source artifact emission and deterministic merge"
    )
    subparsers = parser.add_subparsers(dest="command")

    # emit subcommand
    emit_parser = subparsers.add_parser("emit", help="Emit a per-source artifact")
    emit_parser.add_argument("--source", required=True, help="Source ID (e.g., techcrunch)")
    emit_parser.add_argument("--articles", required=True, help="Path to articles JSON array")
    emit_parser.add_argument("--status", default=None, help="Path to source status JSON (optional)")
    emit_parser.add_argument("--run-context", required=True, help="Path to shared run context JSON")
    emit_parser.add_argument("--output", required=True, help="Output path for per-source artifact")

    # merge subcommand
    merge_parser = subparsers.add_parser("merge", help="Merge per-source artifacts")
    merge_parser.add_argument("--artifacts-dir", required=True, help="Directory containing per-source artifacts")
    merge_parser.add_argument("--run-context", required=True, help="Path to shared run context JSON")
    merge_parser.add_argument("--output", required=True, help="Output path for merged canonical artifact")

    # validate subcommand
    validate_parser = subparsers.add_parser("validate", help="Validate artifacts without merging")
    validate_parser.add_argument("--artifacts-dir", required=True, help="Directory containing per-source artifacts")
    validate_parser.add_argument("--run-context", required=True, help="Path to shared run context JSON")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    if args.command == "emit":
        return cmd_emit(args)
    elif args.command == "merge":
        return cmd_merge(args)
    elif args.command == "validate":
        return cmd_validate(args)
    return 1


if __name__ == "__main__":
    sys.exit(main())
