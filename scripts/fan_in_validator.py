#!/usr/bin/env python3
"""Fan-in validation contract for crawl matrix artifacts.

This module implements the non-publishing fan-in validator that ensures
crawl artifacts (whether from monolithic or matrix legs) meet the
consistency requirements before canonical output is produced.

Validation checks:
- Schema/version consistency across all legs
- Checksum integrity (content checksums match declared values)
- Window consistency (all legs use the same since/until)
- Deterministic ordering (repos by full_name, articles by source+url)
- Duplicate URL/repo handling (dedup with documented priority rules)
- Stale cache rejection (artifacts older than configured max age)
- Source status metadata (required vs optional failure behavior)
- Byte-stable output verification (same inputs → same canonical output)

References:
    - Issue #333: Define crawl matrix readiness and fan-in validation path
    - docs/matrix-crawl-fan-in-contracts.md: Full contract specification
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

from scripts.run_context import RunContext


class FanInContractError(Exception):
    """Raised when a fan-in contract violation is detected."""

    pass


@dataclass(slots=True)
class ValidationResult:
    """Result of fan-in validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifact_count: int = 0
    sources_present: list[str] = field(default_factory=list)
    sources_missing_required: list[str] = field(default_factory=list)
    sources_missing_optional: list[str] = field(default_factory=list)
    duplicate_urls: list[str] = field(default_factory=list)
    duplicate_repos: list[str] = field(default_factory=list)
    stale_artifacts: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "artifact_count": self.artifact_count,
            "sources_present": self.sources_present,
            "sources_missing_required": self.sources_missing_required,
            "sources_missing_optional": self.sources_missing_optional,
            "duplicate_urls": self.duplicate_urls,
            "duplicate_repos": self.duplicate_repos,
            "stale_artifacts": self.stale_artifacts,
        }


# Maximum age of a per-source artifact before it's considered stale
DEFAULT_MAX_ARTIFACT_AGE = timedelta(hours=24)

# Minimum percentage of required sources that must succeed
MINIMUM_SOURCE_SUCCESS_RATIO = 0.6


def validate_artifact_schema(
    artifact: dict[str, Any],
    expected_schema_version: str,
) -> list[str]:
    """Validate artifact schema structure. Returns list of errors."""
    errors: list[str] = []

    if not isinstance(artifact, dict):
        return ["artifact must be a JSON object"]

    sv = artifact.get("schema_version") or artifact.get("source_artifact_schema_version")
    if sv is None:
        errors.append("missing schema_version field")
    elif str(sv) != str(expected_schema_version):
        errors.append(f"schema_version mismatch: expected '{expected_schema_version}', got '{sv}'")

    return errors


def validate_checksum_integrity(artifact: dict[str, Any]) -> list[str]:
    """Verify that declared checksums match computed values."""
    errors: list[str] = []

    # Check artifact_checksum if present
    if "artifact_checksum" in artifact and "articles" in artifact:
        payload = {
            "source_id": artifact.get("source_id", ""),
            "run_context": artifact.get("run_context", {}),
            "articles": artifact.get("articles", []),
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        computed = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        if artifact["artifact_checksum"] != computed:
            errors.append(
                f"artifact_checksum mismatch for source '{artifact.get('source_id', '?')}': "
                f"declared={artifact['artifact_checksum'][:16]}..., computed={computed[:16]}..."
            )

    # Check content_checksum in metrics if present
    if "checksum" in artifact:
        # For GitHub shard artifacts: checksum covers repositories array
        if "repositories" in artifact:
            content = json.dumps(
                artifact["repositories"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
            computed = hashlib.sha256(content.encode("utf-8")).hexdigest()
            if artifact["checksum"] != computed:
                errors.append(f"checksum mismatch for shard '{artifact.get('shard_id', '?')}'")

    return errors


def validate_window_consistency(
    artifacts: list[dict[str, Any]],
    run_context: RunContext | dict[str, Any],
) -> list[str]:
    """Ensure all artifacts share the same crawl window as the run context."""
    errors: list[str] = []

    if isinstance(run_context, RunContext):
        expected_since = run_context.since
        expected_until = run_context.until
        expected_week = run_context.week
    else:
        expected_since = run_context.get("since") or run_context.get("crawl_window", {}).get(
            "since"
        )
        expected_until = run_context.get("until") or run_context.get("crawl_window", {}).get(
            "until"
        )
        expected_week = run_context.get("week", "")

    for i, artifact in enumerate(artifacts):
        ctx = artifact.get("run_context", {})
        source_id = artifact.get("source_id") or artifact.get("shard_id") or f"artifact[{i}]"

        # Check window
        art_since = ctx.get("since") or ctx.get("crawl_window", {}).get("since")
        art_until = ctx.get("until") or ctx.get("crawl_window", {}).get("until")
        art_week = ctx.get("week", "")

        if art_week and art_week != expected_week:
            errors.append(f"{source_id}: week mismatch ({art_week} vs {expected_week})")
        if art_since and art_since != expected_since:
            errors.append(f"{source_id}: since mismatch ({art_since} vs {expected_since})")
        if art_until and art_until != expected_until:
            errors.append(f"{source_id}: until mismatch ({art_until} vs {expected_until})")

    return errors


def validate_deterministic_ordering(articles: list[dict[str, Any]]) -> list[str]:
    """Verify articles are in deterministic order (source_id, url)."""
    errors: list[str] = []

    for i in range(len(articles) - 1):
        key_a = (articles[i].get("source", ""), articles[i].get("url", ""))
        key_b = (articles[i + 1].get("source", ""), articles[i + 1].get("url", ""))
        if key_a > key_b:
            errors.append(f"non-deterministic ordering at index {i}: {key_a} > {key_b}")
            break  # One violation is enough to flag

    return errors


def detect_duplicate_urls(articles: list[dict[str, Any]]) -> list[str]:
    """Find duplicate URLs across all articles."""
    seen: dict[str, int] = {}
    duplicates: list[str] = []

    for article in articles:
        url = _normalize_url(article.get("url", ""))
        if url in seen:
            duplicates.append(url)
        else:
            seen[url] = 1

    return duplicates


def detect_duplicate_repos(repositories: list[dict[str, Any]]) -> list[str]:
    """Find duplicate repository full_names."""
    seen: set[str] = set()
    duplicates: list[str] = []

    for repo in repositories:
        name = repo.get("full_name", "")
        if name in seen:
            duplicates.append(name)
        else:
            seen.add(name)

    return duplicates


def validate_stale_artifacts(
    artifacts: list[dict[str, Any]],
    reference_time: datetime | None = None,
    max_age: timedelta = DEFAULT_MAX_ARTIFACT_AGE,
) -> list[str]:
    """Reject artifacts older than max_age from reference time."""
    stale: list[str] = []
    now = reference_time or datetime.now(UTC)

    for artifact in artifacts:
        crawled_at = artifact.get("crawled_at") or artifact.get("created_at")
        if not crawled_at:
            continue

        try:
            ts = datetime.fromisoformat(crawled_at.replace("Z", "+00:00"))
            if (now - ts) > max_age:
                source_id = artifact.get("source_id") or artifact.get("shard_id") or "unknown"
                stale.append(f"{source_id}: artifact age {now - ts} exceeds max {max_age}")
        except (ValueError, TypeError):
            pass

    return stale


def validate_source_status(
    artifacts: list[dict[str, Any]],
    required_sources: list[str],
    optional_sources: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate source status metadata.

    Returns (errors, warnings):
    - Errors for required sources that are missing or failed
    - Warnings for optional sources that are missing or failed
    """
    errors: list[str] = []
    warnings: list[str] = []
    optional = set(optional_sources or [])

    present_sources: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        source_id = artifact.get("source_id") or artifact.get("shard_id", "")
        present_sources[source_id] = artifact

    # Check required sources
    for source in required_sources:
        if source not in present_sources:
            errors.append(f"required source '{source}' missing")
        else:
            status = present_sources[source].get("status", {})
            if isinstance(status, dict) and not status.get("success", True):
                errors.append(
                    f"required source '{source}' failed: "
                    f"{status.get('error_message', 'unknown error')}"
                )

    # Check optional sources
    for source in optional:
        if source not in present_sources:
            warnings.append(f"optional source '{source}' missing")
        else:
            status = present_sources[source].get("status", {})
            if isinstance(status, dict) and not status.get("success", True):
                warnings.append(
                    f"optional source '{source}' degraded: {status.get('error_message', 'unknown')}"
                )

    return errors, warnings


def verify_byte_stability(
    canonical_output: dict[str, Any],
    reference_output: dict[str, Any],
    exclude_fields: list[str] | None = None,
) -> list[str]:
    """Verify that canonical output is byte-stable compared to reference.

    Excludes documented timestamp fields from comparison.
    """
    errors: list[str] = []
    exclude = set(exclude_fields or ["merged_at", "crawled_at", "created_at"])

    def _strip_excluded(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _strip_excluded(v) for k, v in obj.items() if k not in exclude}
        if isinstance(obj, list):
            return [_strip_excluded(item) for item in obj]
        return obj

    stripped_canonical = _strip_excluded(canonical_output)
    stripped_reference = _strip_excluded(reference_output)

    canonical_json = json.dumps(stripped_canonical, sort_keys=True, separators=(",", ":"))
    reference_json = json.dumps(stripped_reference, sort_keys=True, separators=(",", ":"))

    if canonical_json != reference_json:
        errors.append("byte-stability violation: outputs differ (excluding timestamp fields)")

    return errors


def run_full_validation(
    artifacts: list[dict[str, Any]],
    run_context: RunContext | dict[str, Any],
    *,
    required_sources: list[str] | None = None,
    optional_sources: list[str] | None = None,
    expected_schema_version: str = "1",
    max_artifact_age: timedelta = DEFAULT_MAX_ARTIFACT_AGE,
    reference_time: datetime | None = None,
) -> ValidationResult:
    """Run the complete fan-in validation contract.

    This is the primary entry point for validating a set of crawl artifacts
    before producing canonical merged output.
    """
    result = ValidationResult(valid=True, artifact_count=len(artifacts))

    if not artifacts:
        result.valid = False
        result.errors.append("no artifacts provided")
        return result

    # 1. Schema validation
    for artifact in artifacts:
        schema_errors = validate_artifact_schema(artifact, expected_schema_version)
        result.errors.extend(schema_errors)

    # 2. Checksum integrity
    for artifact in artifacts:
        checksum_errors = validate_checksum_integrity(artifact)
        result.errors.extend(checksum_errors)

    # 3. Window consistency
    window_errors = validate_window_consistency(artifacts, run_context)
    result.errors.extend(window_errors)

    # 4. Stale cache rejection
    stale = validate_stale_artifacts(artifacts, reference_time, max_artifact_age)
    result.stale_artifacts = stale
    result.errors.extend(stale)

    # 5. Source status metadata
    req_sources = required_sources or []
    opt_sources = optional_sources or []
    source_errors, source_warnings = validate_source_status(artifacts, req_sources, opt_sources)
    result.errors.extend(source_errors)
    result.warnings.extend(source_warnings)

    # 6. Track present/missing sources
    result.sources_present = [
        a.get("source_id") or a.get("shard_id") or "unknown" for a in artifacts
    ]
    result.sources_missing_required = [s for s in req_sources if s not in result.sources_present]
    result.sources_missing_optional = [s for s in opt_sources if s not in result.sources_present]

    # 7. Duplicate detection
    all_articles = []
    all_repos = []
    for artifact in artifacts:
        all_articles.extend(artifact.get("articles", []))
        all_repos.extend(artifact.get("repositories", []))

    if all_articles:
        result.duplicate_urls = detect_duplicate_urls(all_articles)
        if result.duplicate_urls:
            result.warnings.append(
                f"duplicate URLs detected ({len(result.duplicate_urls)}): deduplication will apply"
            )

    if all_repos:
        result.duplicate_repos = detect_duplicate_repos(all_repos)
        if result.duplicate_repos:
            result.warnings.append(
                f"duplicate repos detected ({len(result.duplicate_repos)}): "
                f"deduplication will apply"
            )

    # Final verdict
    result.valid = len(result.errors) == 0
    return result


def _normalize_url(url: str) -> str:
    """Normalize URL for deduplication: scheme + host + path (strip query)."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".lower()
