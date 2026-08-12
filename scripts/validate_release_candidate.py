#!/usr/bin/env python3
"""Validate Claracle release-candidate evidence and revision boundaries."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

DEFAULT_RECORD = Path("data/release/claracle-v1.1-release-candidate.json")
DEFAULT_SCHEMA = Path("data/schemas/release-candidate.schema.json")
EVIDENCE_ONLY_PREFIXES = (
    ".copilot-tracking/",
    "data/release/",
    "docs/review/claracle-post-relaunch/",
)


def load_object(path: Path) -> dict[str, Any]:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return loaded


def parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must include a timezone: {value}")
    return parsed.astimezone(timezone.utc)


def changed_paths_after_candidate(root: Path, candidate_sha: str) -> list[str]:
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", candidate_sha, "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ValueError(f"Candidate SHA is not an ancestor of HEAD: {candidate_sha}")
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{candidate_sha}..HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def validate(
    payload: dict[str, Any],
    schema: dict[str, Any],
    *,
    now: datetime | None = None,
    changed_paths: list[str] | None = None,
) -> None:
    errors = sorted(
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
        ).iter_errors(payload),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        path = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise ValueError(f"Schema validation failed at {path}: {errors[0].message}")

    candidate_sha = payload["candidate_sha"]
    status = payload["status"]
    if candidate_sha is None:
        if status != "preparing" or payload["candidate_frozen_at"] is not None:
            raise ValueError("Only a preparing record may omit the candidate SHA")
    elif payload["candidate_frozen_at"] is None:
        raise ValueError("A frozen candidate requires candidate_frozen_at")

    finding_ids = [finding["id"] for finding in payload["findings"]]
    if finding_ids != [f"DRF-0{index}" for index in range(1, 6)]:
        raise ValueError("Findings must contain DRF-01 through DRF-05 in order")

    for finding in payload["findings"]:
        for evidence in finding["evidence"]:
            if evidence["candidate_sha"] != candidate_sha:
                raise ValueError(f"{finding['id']} evidence does not match candidate SHA")
        live_review = finding["live_at_review"]
        if finding["id"] == "DRF-05" and finding["status"] == "closed":
            if live_review is None or live_review["disposition"] != "pass":
                raise ValueError("DRF-05 closure requires a passing live AT review")
            if live_review["candidate_sha"] != candidate_sha:
                raise ValueError("DRF-05 live AT review does not match candidate SHA")

    blocking = [
        finding["id"]
        for finding in payload["findings"]
        if finding["severity"] in {1, 2} and finding["status"] != "closed"
    ]
    sponsor = payload["sponsor"]
    if status in {"go", "deployed"} or sponsor["status"] == "go":
        if candidate_sha is None or blocking:
            raise ValueError(f"GO is blocked by unresolved findings: {blocking}")
        if sponsor["candidate_sha"] != candidate_sha:
            raise ValueError("Sponsor decision does not match candidate SHA")
        if not sponsor["reviewer"] or not sponsor["decided_at"]:
            raise ValueError("Sponsor GO requires reviewer and decision timestamp")

    deployment = payload["deployment"]
    if deployment["status"] == "completed":
        if sponsor["status"] != "go" or status != "deployed":
            raise ValueError("Completed deployment requires sponsor GO and deployed status")
        if not all(
            (
                deployment["merge_sha"],
                deployment["run_id"],
                deployment["deployed_at"],
                deployment["evidence"],
            )
        ):
            raise ValueError("Completed deployment evidence is incomplete")

    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    windows = [outcome["window"] for outcome in payload["outcomes"]]
    expected_windows = ["release-day", "seven-day", "28-day", "three-month", "six-month"]
    if windows != expected_windows:
        raise ValueError("Outcome windows are missing, duplicated, or out of order")
    for outcome in payload["outcomes"]:
        if outcome["status"] == "scheduled" and outcome["due_at"] is None:
            raise ValueError(f"{outcome['window']} scheduled outcome requires due_at")
        if outcome["status"] == "completed":
            if not outcome["due_at"] or not outcome["completed_at"] or not outcome["evidence"]:
                raise ValueError(f"{outcome['window']} completed outcome is incomplete")
            completed_at = parse_timestamp(outcome["completed_at"])
            if completed_at < parse_timestamp(outcome["due_at"]):
                raise ValueError(f"{outcome['window']} cannot be completed before its due date")
            if completed_at > now:
                raise ValueError(f"{outcome['window']} cannot be completed in the future")

    if candidate_sha and changed_paths is not None:
        invalid = [path for path in changed_paths if not path.startswith(EVIDENCE_ONLY_PREFIXES)]
        if invalid:
            raise ValueError(
                "Product or test files changed after candidate freeze: "
                + ", ".join(sorted(invalid))
            )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--check-git-boundary",
        action="store_true",
        help="Reject non-evidence changes committed after the frozen candidate SHA.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    record = args.record if args.record.is_absolute() else root / args.record
    schema_path = args.schema if args.schema.is_absolute() else root / args.schema
    payload = load_object(record)
    changed_paths = None
    if args.check_git_boundary and payload["candidate_sha"]:
        changed_paths = changed_paths_after_candidate(root, payload["candidate_sha"])
    validate(payload, load_object(schema_path), changed_paths=changed_paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
