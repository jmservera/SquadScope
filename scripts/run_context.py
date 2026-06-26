#!/usr/bin/env python3
"""Shared run-context schema for crawl matrix legs and fan-in validation.

This module defines the canonical run-context schema that all crawl legs,
fan-in validators, and downstream consumers share. No matrix leg may
independently compute its own time window from the local wall clock.

The run context is the single source of truth for:
- run_id: stable idempotency key
- week: ISO week identifier
- since/until: inclusive start and exclusive end of the collection window
- config checksums: detect drift between legs
- code_sha: pipeline version pinning

References:
    - Issue #333: Define crawl matrix readiness and fan-in validation path
    - docs/matrix-crawl-fan-in-contracts.md: Full contract specification
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "run_context_v1"

# ISO week pattern: YYYY-WNN
_WEEK_RE = re.compile(r"^\d{4}-W(?:0[1-9]|[1-4]\d|5[0-3])$")

# ISO-8601 timestamp pattern (basic check)
_ISO_TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$")


@dataclass(frozen=True, slots=True)
class RunContext:
    """Immutable shared run context distributed to all crawl legs."""

    schema_version: str
    run_id: str
    week: str
    since: str
    until: str
    source_config_checksum: str
    topic_config_checksum: str
    code_sha: str
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False, **kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RunContext":
        return cls(
            schema_version=data["schema_version"],
            run_id=data["run_id"],
            week=data["week"],
            since=data["since"],
            until=data["until"],
            source_config_checksum=data["source_config_checksum"],
            topic_config_checksum=data["topic_config_checksum"],
            code_sha=data["code_sha"],
            created_at=data["created_at"],
        )

    @classmethod
    def from_json(cls, text: str) -> "RunContext":
        return cls.from_dict(json.loads(text))


class RunContextValidationError(Exception):
    """Raised when run context validation fails."""

    pass


def build_run_context(
    *,
    week: str,
    since: datetime,
    until: datetime,
    source_config_checksum: str,
    topic_config_checksum: str,
    code_sha: str,
    created_at: datetime | None = None,
    run_id: str | None = None,
) -> RunContext:
    """Build an immutable run context for a crawl run.

    The run_id is derived deterministically from the week and checksums
    unless explicitly provided.
    """
    now = created_at or datetime.now(UTC)
    since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    until_str = until.strftime("%Y-%m-%dT%H:%M:%SZ")
    created_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    if run_id is None:
        # Deterministic run_id from week + checksums
        id_payload = f"{week}:{source_config_checksum}:{topic_config_checksum}:{code_sha}"
        sha_prefix = hashlib.sha256(id_payload.encode()).hexdigest()[:12]
        run_id = f"{week}-{sha_prefix}"

    return RunContext(
        schema_version=SCHEMA_VERSION,
        run_id=run_id,
        week=week,
        since=since_str,
        until=until_str,
        source_config_checksum=source_config_checksum,
        topic_config_checksum=topic_config_checksum,
        code_sha=code_sha,
        created_at=created_str,
    )


def validate_run_context(ctx: RunContext | dict[str, Any]) -> list[str]:
    """Validate a run context structure. Returns a list of error strings (empty = valid)."""
    if isinstance(ctx, RunContext):
        data = ctx.to_dict()
    else:
        data = ctx

    errors: list[str] = []

    # Required fields
    required_fields = [
        "schema_version",
        "run_id",
        "week",
        "since",
        "until",
        "source_config_checksum",
        "topic_config_checksum",
        "code_sha",
        "created_at",
    ]
    for f in required_fields:
        if f not in data or not data[f]:
            errors.append(f"missing or empty required field: {f}")

    if errors:
        return errors

    # Schema version
    if data["schema_version"] != SCHEMA_VERSION:
        errors.append(
            f"schema_version mismatch: expected '{SCHEMA_VERSION}', got '{data['schema_version']}'"
        )

    # Week format
    if not _WEEK_RE.match(data["week"]):
        errors.append(f"invalid week format: '{data['week']}' (expected YYYY-WNN)")

    # Timestamp formats
    for ts_field in ("since", "until", "created_at"):
        val = data.get(ts_field, "")
        if val and not _ISO_TS_RE.match(val):
            errors.append(f"invalid ISO-8601 timestamp in '{ts_field}': '{val}'")

    # Checksum format (should be hex strings)
    for cksum_field in ("source_config_checksum", "topic_config_checksum", "code_sha"):
        val = data.get(cksum_field, "")
        if val and not re.match(r"^[a-f0-9]+$", val):
            errors.append(f"invalid hex checksum in '{cksum_field}': '{val}'")

    return errors


def compute_source_config_checksum(config_path: Path) -> str:
    """Compute SHA-256 checksum of the source configuration file."""
    content = config_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def compute_topic_config_checksum(config_path: Path) -> str:
    """Compute SHA-256 checksum of the topic configuration file."""
    content = config_path.read_bytes()
    return hashlib.sha256(content).hexdigest()


def compute_code_sha(source_files: list[Path]) -> str:
    """Compute combined SHA-256 of relevant pipeline source files."""
    h = hashlib.sha256()
    for f in sorted(source_files):
        if f.exists():
            h.update(f.read_bytes())
    return h.hexdigest()


def contexts_compatible(a: RunContext, b: RunContext) -> list[str]:
    """Check if two run contexts are compatible for fan-in merge.

    Returns list of mismatch descriptions (empty = compatible).
    """
    mismatches: list[str] = []

    if a.schema_version != b.schema_version:
        mismatches.append(f"schema_version: {a.schema_version} vs {b.schema_version}")
    if a.week != b.week:
        mismatches.append(f"week: {a.week} vs {b.week}")
    if a.since != b.since:
        mismatches.append(f"since: {a.since} vs {b.since}")
    if a.until != b.until:
        mismatches.append(f"until: {a.until} vs {b.until}")
    if a.source_config_checksum != b.source_config_checksum:
        mismatches.append(
            f"source_config_checksum: {a.source_config_checksum} vs {b.source_config_checksum}"
        )
    if a.topic_config_checksum != b.topic_config_checksum:
        mismatches.append(
            f"topic_config_checksum: {a.topic_config_checksum} vs {b.topic_config_checksum}"
        )
    if a.code_sha != b.code_sha:
        mismatches.append(f"code_sha: {a.code_sha} vs {b.code_sha}")

    return mismatches
